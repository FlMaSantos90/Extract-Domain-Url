import os
import re
import time
from urllib.parse import urlparse
import tkinter as tk
from tkinter import filedialog
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.text import Text
from rich.align import Align
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import io
import multiprocessing as mp

console = Console()

def is_valid_email(email):
    if not email:
        return False
    if '@' not in email or '.' not in email:
        return False
    pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return pattern.match(email) is not None

def get_root_url(url_string):
    if not url_string.startswith(('http://', 'https://')):
        url_string = 'http://' + url_string
    parsed_url = urlparse(url_string)
    return parsed_url.netloc + '/'

def create_progress_bar_mb(total_mb):
    progress = Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[bold cyan]{task.description}[/bold cyan]"),
        BarColumn(bar_width=30),
        TextColumn("[bold green]{task.percentage:>3.0f}%[/bold green]"),
        TextColumn("[bold magenta]{task.completed:.1f}/{task.total:.1f} MB[/bold magenta]"),
        TextColumn("[bold yellow]{task.fields[speed]}[/bold yellow] |"),
        TimeElapsedColumn(),
        TextColumn(" ~ "),
        TimeRemainingColumn(),
        console=console,
        transient=False
    )
    return progress

def analyze_file_ultra_fast(file_path):
    filename = os.path.basename(file_path)
    file_size_mb = os.path.getsize(file_path) / (1024*1024)
    
    analyze_progress = Progress(
        SpinnerColumn(spinner_name="point"),
        TextColumn("[bold magenta]Đang đọc file...[/bold magenta]"),
        TextColumn("[bold cyan]{task.completed:.1f}MB/{task.total:.1f}MB[/bold cyan]"),
        BarColumn(bar_width=20),
        TextColumn("[bold green]{task.percentage:>3.0f}%[/bold green]"),
        console=console,
        transient=True
    )
    
    total_lines = 0
    bytes_read = 0
    
    with analyze_progress:
        task = analyze_progress.add_task("analyzing", total=file_size_mb, completed=0)
        
        try:
            with open(file_path, 'rb') as f:
                chunk_size = 4194304
                last_update = time.time()
                
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    
                    total_lines += chunk.count(b'\n')
                    bytes_read += len(chunk)
                    
                    current_time = time.time()
                    if current_time - last_update >= 0.01:
                        mb_read = bytes_read / (1024 * 1024)
                        analyze_progress.update(task, completed=mb_read)
                        last_update = current_time
                
                analyze_progress.update(task, completed=file_size_mb)
                time.sleep(0.05)
        
        except Exception:
            return 0
    
    return total_lines

def process_chunk_optimized(args):
    chunk_data, choice = args
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    lines = chunk_data.split('\n')
    valid_lines = []
    invalid_count = 0
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        try:
            colon_count = line.count(':')
            if colon_count < 2:
                invalid_count += 1
                continue
                
            last_colon = line.rfind(':')
            second_last_colon = line.rfind(':', 0, last_colon)
            
            if second_last_colon == -1:
                invalid_count += 1
                continue
                
            url_part = line[:second_last_colon]
            email_part = line[second_last_colon+1:last_colon]
            pass_part = line[last_colon+1:]
            
            if '@' not in email_part or '.' not in email_part:
                invalid_count += 1
                continue
            
            if not email_pattern.match(email_part):
                invalid_count += 1
                continue
            
            if choice == '1':
                if not url_part.startswith(('http://', 'https://')):
                    url_part = 'http://' + url_part
                parsed_url = urlparse(url_part)
                root_url = parsed_url.netloc + '/'
                new_line = f"{root_url}:{email_part}:{pass_part}"
            else:
                new_line = f"{email_part}:{pass_part}"
            
            valid_lines.append(new_line)
            
        except:
            invalid_count += 1
    
    return valid_lines, invalid_count

def process_file_ultra_fast(input_path, output_path, choice):
    total_lines = analyze_file_ultra_fast(input_path)
    file_size_mb = os.path.getsize(input_path) / (1024 * 1024)
    
    if total_lines == 0:
        console.print(f"\n[bold red][Lỗi] Không thể đọc tệp hoặc tệp rỗng: '{input_path}'[/bold red]")
        return

    info_text = Text()
    info_text.append("⚡ EXTRA t.me/anhduc07⚡ | ", style="bold red")
    info_text.append("📁 ", style="bold blue")
    info_text.append(f"{os.path.basename(input_path)}", style="bold cyan")
    info_text.append(f" | 💾 {file_size_mb:.1f} MB", style="bold green")
    info_text.append(f" | 📊 {total_lines:,} dòng", style="bold yellow")
    
    console.print(Align.center(info_text))
    console.print()

    progress = create_progress_bar_mb(file_size_mb)
    
    lines_processed = 0
    lines_invalid = 0
    bytes_processed = 0
    
    output_chunks = []
    
    try:
        with open(input_path, 'r', encoding='utf-8', buffering=8388608) as infile, \
             progress:

            task_id = progress.add_task("Đang xử lý", total=file_size_mb, speed="0 MB/s")
            start_time = time.time()
            last_update_time = start_time

            chunk_size = 8388608
            buffer = ""
            
            cpu_count = min(mp.cpu_count(), 8)
            
            with ProcessPoolExecutor(max_workers=cpu_count) as executor:
                futures = []
                chunk_args = []
                
                while True:
                    chunk = infile.read(chunk_size)
                    if not chunk:
                        if buffer.strip():
                            chunk_args.append((buffer, choice))
                        break
                    
                    buffer += chunk
                    bytes_processed += len(chunk.encode('utf-8'))
                    
                    newline_pos = buffer.rfind('\n')
                    if newline_pos != -1:
                        complete_chunk = buffer[:newline_pos]
                        buffer = buffer[newline_pos + 1:]
                        
                        chunk_args.append((complete_chunk, choice))
                        
                        if len(chunk_args) >= cpu_count * 2:
                            batch_futures = [executor.submit(process_chunk_optimized, arg) for arg in chunk_args]
                            futures.extend(batch_futures)
                            chunk_args = []
                    
                    if len(futures) >= cpu_count * 4:
                        completed_futures = []
                        for future in futures[:cpu_count]:
                            if future.done():
                                valid_lines, invalid_count = future.result()
                                output_chunks.extend(valid_lines)
                                lines_processed += len(valid_lines)
                                lines_invalid += invalid_count
                                completed_futures.append(future)
                        
                        for future in completed_futures:
                            futures.remove(future)
                    
                    current_time = time.time()
                    if current_time - last_update_time >= 0.02:
                        mb_processed = bytes_processed / (1024 * 1024)
                        elapsed = current_time - start_time
                        speed_mb = f"{mb_processed / elapsed:.1f} MB/s" if elapsed > 0 else "0 MB/s"
                        
                        progress.update(
                            task_id, 
                            completed=mb_processed,
                            speed=speed_mb
                        )
                        last_update_time = current_time
                
                if chunk_args:
                    batch_futures = [executor.submit(process_chunk_optimized, arg) for arg in chunk_args]
                    futures.extend(batch_futures)
                
                for future in futures:
                    valid_lines, invalid_count = future.result()
                    output_chunks.extend(valid_lines)
                    lines_processed += len(valid_lines)
                    lines_invalid += invalid_count
            
            with open(output_path, 'w', encoding='utf-8', buffering=8388608) as outfile:
                batch_size = 50000
                for i in range(0, len(output_chunks), batch_size):
                    batch = output_chunks[i:i+batch_size]
                    outfile.write('\n'.join(batch) + '\n')
            
            elapsed = time.time() - start_time
            speed_mb = f"{file_size_mb / elapsed:.1f} MB/s" if elapsed > 0 else "0 MB/s"
            speed_lines = f"{int((lines_processed + lines_invalid) / elapsed):,} dòng/s" if elapsed > 0 else "0 dòng/s"
            
            progress.update(
                task_id, 
                completed=file_size_mb,
                speed=speed_mb
            )
    
    except FileNotFoundError:
        console.print(f"\n[bold red][Lỗi] Không tìm thấy tệp '{input_path}'.[/bold red]")
        return
    except Exception as e:
        console.print(f"\n[bold red][Lỗi] {e}[/bold red]")
        return

    console.print("\n[bold green]🚀 Xử lý siêu tốc hoàn tất![/bold green]")
    console.print(f"✅ Dòng hợp lệ: [bold green]{lines_processed:,}[/bold green]")
    console.print(f"❌ Dòng loại bỏ: [bold yellow]{lines_invalid:,}[/bold yellow]")
    console.print(f"📈 Tỷ lệ thành công: [bold cyan]{(lines_processed / total_lines * 100):.1f}%[/bold cyan]")
    console.print(f"⚡ Tốc độ trung bình: [bold magenta]{speed_lines}[/bold magenta]")
    console.print(f"💾 Kết quả: [bold cyan]'{output_path}'[/bold cyan]")

def main():
    mp.set_start_method('spawn', force=True)
    
    root = tk.Tk()
    root.withdraw() 

    input_file = filedialog.askopenfilename(
        title="Chọn tệp dữ liệu (.txt)",
        filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
    )

    if not input_file:
        console.print("\n[yellow]Hủy bỏ.[/yellow]")
        return 

    console.print("\n[bold]Chọn chế độ xử lý:[/bold]")
    console.print("  [cyan]1.[/cyan] Giữ URL rút gọn | [italic]domain:email:pass[/italic]")
    console.print("  [cyan]2.[/cyan] Chỉ email:pass | [italic]email:pass[/italic]")
    
    choice = ''
    while choice not in ['1', '2']:
        choice = console.input("[bold]Chọn (1 hoặc 2): [/bold]")

    base_name, ext = os.path.splitext(input_file)
    output_file = f"{base_name}_ket_qua_da_loc.txt"

    console.print()
    
    process_file_ultra_fast(input_file, output_file, choice)
    
    console.print("\n" + "=" * 60)
    console.input("[italic]Nhấn Enter để thoát.[/italic]")

if __name__ == "__main__":
    main()
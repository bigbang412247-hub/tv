import tkinter as tk
from tkinter import filedialog, messagebox
import re
import subprocess
import threading
import os
import urllib.request
import time

class RakibPersonalTV:
    def __init__(self, root):
        self.root = root
        self.root.title("রাকিবের পার্সোনাল স্মার্ট টিভি")
        self.root.geometry("1500x850")
        self.root.minsize(1200, 700)
        self.root.configure(bg='#0a0e17')
        
        # ==================================================
        # ⭐⭐⭐ কাস্টম আইকন সেট করা (tv.ico) ⭐⭐⭐
        # ==================================================
        try:
            # আপনার দেওয়া পাথ থেকে আইকন লোড
            icon_path = r"C:\Users\bigbang\OneDrive\Desktop\hello\tv.ico"
            if os.path.exists(icon_path):
                self.root.iconbitmap(default=icon_path)
                print(f"✅ আইকন লোড হয়েছে: {icon_path}")
            else:
                # যদি ফাইল না থাকে, ট্রান্সপারেন্ট আইকন ব্যবহার
                empty_icon = tk.PhotoImage(width=1, height=1)
                self.root.iconphoto(True, empty_icon)
                print(f"⚠️ আইকন ফাইল পাওয়া যায়নি: {icon_path}")
        except Exception as e:
            # এরর হলে ট্রান্সপারেন্ট আইকন
            try:
                empty_icon = tk.PhotoImage(width=1, height=1)
                self.root.iconphoto(True, empty_icon)
            except:
                pass
            print(f"❌ আইকন সেট করতে সমস্যা: {e}")
        # ==================================================
        
        # থিম কালার
        self.colors = {
            'bg': '#0a0e17',
            'bg2': '#111827',
            'bg3': '#1a2332',
            'header': '#0d1520',
            'card': '#162036',
            'card_hover': '#1e2d4a',
            'accent': '#ff6b35',
            'accent2': '#00d4ff',
            'accent3': '#ffd700',
            'green': '#22c55e',
            'red': '#ef4444',
            'text': '#ffffff',
            'text_light': '#94a3b8',
            'text_muted': '#475569',
            'border': '#1e2d4a',
            'gold': '#ffd700',
            'sports': '#ff6b35',
            'fifa': '#ffd700'
        }
        
        # ভেরিয়েবল
        self.channels = []
        self.categories = {}
        self.working_channels = []
        self.sports_channels = []
        self.fifa_channels = []
        self.current_channel = None
        self.player_process = None
        self.is_playing = False
        self.is_checking = False
        self.video_window = None
        
        # mpv পাথ
        self.mpv_path = self.find_mpv()
        
        # UI তৈরি
        self.create_ui()
        
        if self.mpv_path:
            self.status_label.config(text="✅ স্মার্ট টিভি প্রস্তুত")
        else:
            self.status_label.config(text="⚠️ MPV ইনস্টল করুন: https://mpv.net/")
    
    def find_mpv(self):
        """MPV খোঁজা"""
        paths = [
            r"C:\Program Files\mpv.net\mpvnet.exe",
            r"C:\Program Files\mpv\mpv.exe",
            r"C:\Program Files (x86)\mpv.net\mpvnet.exe",
            r"C:\mpv.net\mpvnet.exe",
            r"C:\mpv\mpv.exe",
        ]
        
        for path in paths:
            if os.path.exists(path):
                return path
        
        try:
            result = subprocess.run(['where', 'mpv'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except:
            pass
        
        return None
    
    def create_ui(self):
        """UI তৈরি - ভিডিও প্লেয়ার ডান পাশে ফিক্সড"""
        
        # === হেডার ===
        header = tk.Frame(self.root, bg=self.colors['header'], height=65)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        # লোগো
        logo_frame = tk.Frame(header, bg=self.colors['header'])
        logo_frame.pack(side='left', padx=25, pady=10)
        
        # শুধু টেক্সট লোগো
        title = tk.Label(logo_frame, text="রাকিবের পার্সোনাল স্মার্ট টিভি", 
                        bg=self.colors['header'], fg='white',
                        font=('Segoe UI', 18, 'bold'))
        title.pack(side='left')
        
        smart_label = tk.Label(logo_frame, text="⚡ SMART TV", 
                              bg=self.colors['header'], fg=self.colors['accent2'],
                              font=('Segoe UI', 10, 'bold'))
        smart_label.pack(side='left', padx=(10, 0))
        
        # মিডল সেকশন - URL ইনপুট
        url_frame = tk.Frame(header, bg=self.colors['header'])
        url_frame.pack(side='left', padx=15)
        
        url_bg = tk.Frame(url_frame, bg=self.colors['bg3'], relief='flat', bd=0)
        url_bg.pack()
        
        self.url_entry = tk.Entry(url_bg, width=28,
                                 bg=self.colors['bg3'], fg='white',
                                 font=('Segoe UI', 11), relief='flat',
                                 insertbackground='white')
        self.url_entry.pack(side='left', padx=10, ipady=6)
        self.url_entry.insert(0, "🔗 URL পেস্ট করুন...")
        self.url_entry.bind('<FocusIn>', lambda e: self.url_entry.select_range(0, tk.END))
        self.url_entry.bind('<Return>', lambda e: self.play_url())
        
        play_url_btn = tk.Button(url_bg, text="▶ প্লে",
                                bg=self.colors['accent'], fg='white',
                                font=('Segoe UI', 10, 'bold'),
                                padx=12, relief='flat',
                                cursor='hand2', command=self.play_url)
        play_url_btn.pack(side='left', padx=(0, 5))
        play_url_btn.bind('<Enter>', lambda e: play_url_btn.config(bg='#ff7a4a'))
        play_url_btn.bind('<Leave>', lambda e: play_url_btn.config(bg=self.colors['accent']))
        
        # রাইট সেকশন
        right_header = tk.Frame(header, bg=self.colors['header'])
        right_header.pack(side='right', padx=20)
        
        # আপলোড বাটন
        upload_btn = tk.Button(right_header, text="📂 M3U ফাইল",
                              bg=self.colors['accent'], fg='white',
                              font=('Segoe UI', 10, 'bold'),
                              padx=15, pady=5, relief='flat',
                              cursor='hand2', command=self.upload_file)
        upload_btn.pack(side='left', padx=5)
        upload_btn.bind('<Enter>', lambda e: upload_btn.config(bg='#ff7a4a'))
        upload_btn.bind('<Leave>', lambda e: upload_btn.config(bg=self.colors['accent']))
        
        # চ্যানেল কাউন্ট
        self.count_label = tk.Label(right_header, text="লাইভ: ০টি চ্যানেল",
                                   bg=self.colors['bg3'], fg=self.colors['green'],
                                   font=('Segoe UI', 10), padx=12, pady=3)
        self.count_label.pack(side='left', padx=5)
        
        # === মেইন কন্টেন্ট ===
        content = tk.Frame(self.root, bg=self.colors['bg'])
        content.pack(fill='both', expand=True, padx=4, pady=4)
        
        # === বাম প্যানেল (ক্যাটাগরি + চ্যানেল) - 35% ===
        left_panel = tk.Frame(content, bg=self.colors['bg'], width=450)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 4))
        left_panel.pack_propagate(False)
        
        # ক্যাটাগরি সেকশন
        cat_section = tk.Frame(left_panel, bg=self.colors['bg'])
        cat_section.pack(fill='x', pady=(0, 4))
        
        # ক্যাটাগরি হেডার
        cat_header_frame = tk.Frame(cat_section, bg=self.colors['bg2'], height=38)
        cat_header_frame.pack(fill='x')
        cat_header_frame.pack_propagate(False)
        
        cat_header = tk.Label(cat_header_frame, text="📂 ক্যাটাগরি সমূহ", 
                             bg=self.colors['bg2'], fg='white',
                             font=('Segoe UI', 12, 'bold'))
        cat_header.pack(side='left', padx=15, pady=8)
        
        # ক্যাটাগরি লিস্ট (স্ক্রলেবল)
        cat_frame = tk.Frame(cat_section, bg=self.colors['bg'], height=120)
        cat_frame.pack(fill='x', pady=(2, 4))
        cat_frame.pack_propagate(False)
        
        cat_scroll = tk.Scrollbar(cat_frame, bg=self.colors['bg'],
                                 troughcolor=self.colors['bg'], width=6)
        cat_scroll.pack(side='right', fill='y')
        
        self.category_list = tk.Listbox(cat_frame, bg=self.colors['bg'],
                                       fg=self.colors['text_light'],
                                       selectbackground=self.colors['accent'],
                                       selectforeground='white',
                                       font=('Segoe UI', 10),
                                       relief='flat', borderwidth=0,
                                       highlightthickness=0,
                                       yscrollcommand=cat_scroll.set,
                                       activestyle='none',
                                       height=5)
        self.category_list.pack(side='left', fill='both', expand=True)
        cat_scroll.config(command=self.category_list.yview)
        self.category_list.bind('<<ListboxSelect>>', self.on_category_select)
        
        # চ্যানেল সেকশন
        ch_section = tk.Frame(left_panel, bg=self.colors['bg'])
        ch_section.pack(fill='both', expand=True)
        
        # চ্যানেল হেডার
        ch_header_frame = tk.Frame(ch_section, bg=self.colors['bg2'], height=38)
        ch_header_frame.pack(fill='x')
        ch_header_frame.pack_propagate(False)
        
        ch_header = tk.Label(ch_header_frame, text="📺 লাইভ চ্যানেল", 
                            bg=self.colors['bg2'], fg='white',
                            font=('Segoe UI', 12, 'bold'))
        ch_header.pack(side='left', padx=15, pady=8)
        
        self.ch_count_label = tk.Label(ch_header_frame, text="০টি চ্যানেল",
                                      bg=self.colors['bg2'], fg=self.colors['green'],
                                      font=('Segoe UI', 10))
        self.ch_count_label.pack(side='right', padx=15, pady=8)
        
        # সার্চ
        search_frame = tk.Frame(ch_section, bg=self.colors['bg'])
        search_frame.pack(fill='x', pady=(4, 4))
        
        search_bg = tk.Frame(search_frame, bg=self.colors['bg2'], relief='flat', bd=0)
        search_bg.pack(fill='x', padx=2)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.search_channels)
        
        search_entry = tk.Entry(search_bg, textvariable=self.search_var,
                               bg=self.colors['bg2'], fg='white',
                               font=('Segoe UI', 10), relief='flat')
        search_entry.pack(fill='x', padx=10, ipady=5)
        search_entry.insert(0, "🔍 চ্যানেল খুঁজুন...")
        
        def on_focus_in(e):
            if search_entry.get() == "🔍 চ্যানেল খুঁজুন...":
                search_entry.delete(0, tk.END)
                search_entry.config(fg='white')
        
        def on_focus_out(e):
            if search_entry.get() == "":
                search_entry.insert(0, "🔍 চ্যানেল খুঁজুন...")
                search_entry.config(fg=self.colors['text_muted'])
        
        search_entry.bind('<FocusIn>', on_focus_in)
        search_entry.bind('<FocusOut>', on_focus_out)
        
        # চ্যানেল লিস্ট (স্ক্রলেবল)
        ch_list_frame = tk.Frame(ch_section, bg=self.colors['bg'])
        ch_list_frame.pack(fill='both', expand=True)
        
        ch_scroll = tk.Scrollbar(ch_list_frame, bg=self.colors['bg'],
                                troughcolor=self.colors['bg'], width=8)
        ch_scroll.pack(side='right', fill='y')
        
        self.channel_list = tk.Listbox(ch_list_frame, bg=self.colors['bg'],
                                       fg=self.colors['text'],
                                       selectbackground=self.colors['accent'],
                                       selectforeground='white',
                                       font=('Segoe UI', 11),
                                       relief='flat', borderwidth=0,
                                       highlightthickness=0,
                                       yscrollcommand=ch_scroll.set,
                                       activestyle='none')
        self.channel_list.pack(side='left', fill='both', expand=True)
        ch_scroll.config(command=self.channel_list.yview)
        self.channel_list.bind('<Double-Button-1>', self.play_selected)
        self.channel_list.bind('<Return>', self.play_selected)
        
        # === ডান প্যানেল (ভিডিও প্লেয়ার) - 65% ফিক্সড ===
        right_panel = tk.Frame(content, bg='#000000')
        right_panel.pack(side='right', fill='both', expand=True)
        
        # ভিডিও প্লেয়ার ফ্রেম
        self.video_frame = tk.Frame(right_panel, bg='#000000')
        self.video_frame.pack(fill='both', expand=True)
        
        # ভিডিও কন্ট্রোল বার (ভিতরে)
        video_control = tk.Frame(self.video_frame, bg='#0a0e17', height=35)
        video_control.pack(side='bottom', fill='x')
        video_control.pack_propagate(False)
        
        # ভিডিও প্লেয়ার ডিসপ্লে
        self.video_display = tk.Frame(self.video_frame, bg='#000000')
        self.video_display.pack(side='top', fill='both', expand=True)
        
        # স্প্ল্যাশ স্ক্রিন
        self.splash_screen()
        
        # ভিডিও কন্ট্রোল বাটন
        vc_left = tk.Frame(video_control, bg='#0a0e17')
        vc_left.pack(side='left', padx=10)
        
        self.now_playing_video = tk.Label(vc_left, text="⏸ কিছু বাজছে না",
                                         bg='#0a0e17', fg=self.colors['text_light'],
                                         font=('Segoe UI', 10))
        self.now_playing_video.pack(side='left')
        
        vc_right = tk.Frame(video_control, bg='#0a0e17')
        vc_right.pack(side='right', padx=10)
        
        # প্লে/পজ বাটন
        self.video_play_btn = tk.Button(vc_right, text="▶",
                                       bg='#0a0e17', fg='white',
                                       font=('Segoe UI', 12), relief='flat',
                                       cursor='hand2', padx=8,
                                       command=self.toggle_play)
        self.video_play_btn.pack(side='left', padx=2)
        self.video_play_btn.bind('<Enter>', lambda e: self.video_play_btn.config(bg='#1a2332'))
        self.video_play_btn.bind('<Leave>', lambda e: self.video_play_btn.config(bg='#0a0e17'))
        
        video_stop_btn = tk.Button(vc_right, text="⏹",
                                  bg='#0a0e17', fg='white',
                                  font=('Segoe UI', 12), relief='flat',
                                  cursor='hand2', padx=8,
                                  command=self.stop_playback)
        video_stop_btn.pack(side='left', padx=2)
        video_stop_btn.bind('<Enter>', lambda e: video_stop_btn.config(bg='#1a2332'))
        video_stop_btn.bind('<Leave>', lambda e: video_stop_btn.config(bg='#0a0e17'))
        
        # ভলিউম
        vol_label = tk.Label(vc_right, text="🔊", bg='#0a0e17',
                            fg='white', font=('Segoe UI', 10))
        vol_label.pack(side='left', padx=(8, 3))
        
        self.video_volume = tk.Scale(vc_right, from_=0, to=100,
                                     orient='horizontal', length=70,
                                     bg='#0a0e17', fg='white',
                                     highlightthickness=0,
                                     relief='flat', cursor='hand2')
        self.video_volume.set(70)
        self.video_volume.pack(side='left')
        
        # === ফুটার ===
        footer = tk.Frame(self.root, bg=self.colors['header'], height=28)
        footer.pack(side='bottom', fill='x')
        footer.pack_propagate(False)
        
        footer_left = tk.Frame(footer, bg=self.colors['header'])
        footer_left.pack(side='left', padx=15)
        
        tk.Label(footer_left, text="📺 রাকিবের পার্সোনাল স্মার্ট টিভি v2.0", 
                bg=self.colors['header'], fg=self.colors['text_muted'],
                font=('Segoe UI', 9)).pack(side='left')
        
        tk.Label(footer_left, text="|", 
                bg=self.colors['header'], fg=self.colors['text_muted'],
                font=('Segoe UI', 9)).pack(side='left', padx=8)
        
        tk.Label(footer_left, text="⚡ লাইভ স্পোর্টস • FIFA World Cup 2026", 
                bg=self.colors['header'], fg=self.colors['gold'],
                font=('Segoe UI', 9, 'bold')).pack(side='left')
        
        footer_right = tk.Frame(footer, bg=self.colors['header'])
        footer_right.pack(side='right', padx=15)
        
        # 📞 01612677826
        tk.Label(footer_right, text="📞 01612677826", 
                bg=self.colors['header'], fg=self.colors['text_light'],
                font=('Segoe UI', 9)).pack(side='left')
        
        tk.Label(footer_right, text="|", 
                bg=self.colors['header'], fg=self.colors['text_muted'],
                font=('Segoe UI', 9)).pack(side='left', padx=8)
        
        self.status_label = tk.Label(footer_right, text="✅ প্রস্তুত",
                                    bg=self.colors['header'], fg=self.colors['green'],
                                    font=('Segoe UI', 9))
        self.status_label.pack(side='left')
    
    def splash_screen(self):
        """স্প্ল্যাশ স্ক্রিন"""
        for widget in self.video_display.winfo_children():
            widget.destroy()
        
        splash_frame = tk.Frame(self.video_display, bg='#000000')
        splash_frame.pack(fill='both', expand=True)
        
        # বড় টেক্সট লোগো
        title = tk.Label(splash_frame, text="রাকিবের পার্সোনাল স্মার্ট টিভি", 
                        bg='#000000', fg='white', font=('Segoe UI', 28, 'bold'))
        title.pack(pady=(100, 10))
        
        sub = tk.Label(splash_frame, text="⚡ লাইভ স্ট্রিম • স্পোর্টস • বিনোদন", 
                      bg='#000000', fg=self.colors['text_light'],
                      font=('Segoe UI', 16))
        sub.pack(pady=5)
        
        info = tk.Label(splash_frame, text="\n📺 চ্যানেল নির্বাচন করুন\n🔗 URL পেস্ট করুন", 
                       bg='#000000', fg=self.colors['text_muted'],
                       font=('Segoe UI', 13))
        info.pack(pady=15)
        
        footer_text = tk.Label(splash_frame, text="📞 01612677826", 
                              bg='#000000', fg=self.colors['text_muted'],
                              font=('Segoe UI', 11))
        footer_text.pack(pady=20)
    
    def upload_file(self):
        """M3U ফাইল আপলোড"""
        file_path = filedialog.askopenfilename(
            title="M3U ফাইল নির্বাচন করুন",
            filetypes=[("M3U files", "*.m3u *.m3u8"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        self.status_label.config(text="⏳ ফাইল পড়া হচ্ছে...")
        self.root.update()
        
        try:
            encodings = ['utf-8', 'utf-8-sig', 'windows-1252', 'latin-1', 
                        'cp1256', 'iso-8859-1', 'gb2312', 'big5']
            content = None
            
            for enc in encodings:
                try:
                    with open(file_path, 'r', encoding=enc, errors='ignore') as f:
                        content = f.read()
                    break
                except:
                    continue
            
            if content is None:
                messagebox.showerror("এরর", "ফাইল পড়া যায়নি!")
                self.status_label.config(text="❌ ফাইল পড়া যায়নি")
                return
            
            self.parse_m3u(content)
            self.update_categories()
            
            if len(self.channels) == 0:
                messagebox.showwarning("সতর্কতা", "কোনো চ্যানেল পাওয়া যায়নি!")
                self.status_label.config(text="❌ কোনো চ্যানেল নেই")
            else:
                self.count_label.config(text=f"লাইভ: ০টি চ্যানেল (চেক হচ্ছে...)")
                self.status_label.config(text="🔄 চ্যানেল চেক করা হচ্ছে...")
                
                threading.Thread(target=self.check_channels, daemon=True).start()
                
                messagebox.showinfo("সফল", f"{len(self.channels)}টি চ্যানেল লোড হয়েছে!\n\n🔄 লাইভ চ্যানেল চেক করা হচ্ছে...")
            
        except Exception as e:
            self.status_label.config(text=f"❌ {str(e)}")
            messagebox.showerror("এরর", str(e))
    
    def parse_m3u(self, content):
        """M3U পার্স"""
        self.channels = []
        self.categories = {}
        self.sports_channels = []
        self.fifa_channels = []
        
        lines = content.split('\n')
        
        sports_keywords = ['sport', 'cricket', 'football', 'fifa', 'world cup', 
                          'espn', 'sky sport', 'tennis', 'basketball', 'hockey',
                          'খেলা', 'ক্রিকেট', 'ফুটবল', 'ফিফা', 'ওয়ার্ল্ড কাপ',
                          'worldcup', 'live sport', 'match', 'game', 'highlights']
        
        fifa_keywords = ['fifa', 'world cup', 'ফিফা', 'ওয়ার্ল্ড কাপ', 'qatar', 
                        'worldcup', 'fifa world']
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith('#EXTINF:'):
                name = self.get_name(line)
                
                category = 'General'
                match = re.search(r'group-title="([^"]+)"', line)
                if match:
                    category = match.group(1).strip()
                
                url = ''
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not next_line.startswith('#'):
                        url = next_line
                        i += 1
                
                if not url:
                    url_match = re.search(r'(https?://[^\s]+)', line)
                    if url_match:
                        url = url_match.group(1)
                
                if url and url.startswith(('http', 'https')):
                    channel = {
                        'name': name,
                        'url': url,
                        'category': category,
                        'working': False,
                        'checked': False
                    }
                    self.channels.append(channel)
                    
                    if category not in self.categories:
                        self.categories[category] = []
                    self.categories[category].append(channel)
                    
                    name_lower = name.lower()
                    category_lower = category.lower()
                    
                    is_sports = False
                    for kw in sports_keywords:
                        if kw in name_lower or kw in category_lower:
                            is_sports = True
                            break
                    
                    if is_sports:
                        self.sports_channels.append(channel)
                    
                    is_fifa = False
                    for kw in fifa_keywords:
                        if kw in name_lower:
                            is_fifa = True
                            break
                    
                    if is_fifa:
                        self.fifa_channels.append(channel)
            
            i += 1
        
        self.categories = dict(sorted(self.categories.items()))
    
    def get_name(self, line):
        """চ্যানেলের নাম"""
        if ',' in line:
            parts = line.split(',', 1)
            if len(parts) > 1:
                name = parts[1].strip()
                if name and not name.startswith('http'):
                    return name
        
        match = re.search(r'tvg-name="([^"]+)"', line)
        if match:
            return match.group(1)
        
        match = re.search(r'group-title="([^"]+)"', line)
        if match:
            return match.group(1)
        
        return f"চ্যানেল {len(self.channels) + 1}"
    
    def check_channels(self):
        """চ্যানেল চেক - শুধু কাজ করা চ্যানেল রাখবে"""
        self.is_checking = True
        self.working_channels = []
        
        total = len(self.channels)
        
        for idx, channel in enumerate(self.channels):
            if idx % 5 == 0:
                self.root.after(0, lambda i=idx: self.status_label.config(
                    text=f"🔄 চেক করা হচ্ছে... {i+1}/{total}"))
            
            try:
                req = urllib.request.Request(channel['url'], method='HEAD')
                req.add_header('User-Agent', 'Mozilla/5.0')
                response = urllib.request.urlopen(req, timeout=3)
                if response.getcode() in [200, 302, 301]:
                    channel['working'] = True
                    self.working_channels.append(channel)
                else:
                    channel['working'] = False
            except:
                channel['working'] = False
        
        self.is_checking = False
        
        # শুধু কাজ করা চ্যানেল রাখি
        self.channels = self.working_channels.copy()
        
        # ক্যাটাগরি রিবিল্ড
        self.categories = {}
        self.sports_channels = []
        self.fifa_channels = []
        
        for ch in self.channels:
            cat = ch['category']
            if cat not in self.categories:
                self.categories[cat] = []
            self.categories[cat].append(ch)
            
            name_lower = ch['name'].lower()
            cat_lower = ch['category'].lower()
            sports_keywords = ['sport', 'cricket', 'football', 'fifa', 'world cup', 
                              'espn', 'sky sport', 'tennis', 'basketball', 'hockey',
                              'খেলা', 'ক্রিকেট', 'ফুটবল', 'ফিফা', 'ওয়ার্ল্ড কাপ']
            for kw in sports_keywords:
                if kw in name_lower or kw in cat_lower:
                    self.sports_channels.append(ch)
                    break
            
            fifa_keywords = ['fifa', 'world cup', 'ফিফা', 'ওয়ার্ল্ড কাপ']
            for kw in fifa_keywords:
                if kw in name_lower:
                    self.fifa_channels.append(ch)
                    break
        
        # খালি ক্যাটাগরি বাদ
        self.categories = {k: v for k, v in self.categories.items() if v}
        
        self.root.after(0, self.finish_check)
    
    def finish_check(self):
        """চেক শেষ"""
        working_count = len(self.channels)
        
        if working_count > 0:
            self.count_label.config(text=f"লাইভ: {working_count}টি চ্যানেল")
            self.status_label.config(text=f"✅ {working_count}টি লাইভ চ্যানেল পাওয়া গেছে")
        else:
            self.count_label.config(text="লাইভ: ০টি চ্যানেল")
            self.status_label.config(text="⚠️ কোন লাইভ চ্যানেল পাওয়া যায়নি!")
        
        self.update_categories()
        
        if self.category_list.size() > 0:
            self.category_list.selection_set(0)
            self.on_category_select(None)
    
    def update_categories(self):
        """ক্যাটাগরি আপডেট - শুধু যেই ক্যাটাগরিতে চ্যানেল আছে"""
        self.category_list.delete(0, tk.END)
        
        if self.fifa_channels:
            self.category_list.insert(tk.END, f"🏆 FIFA World Cup ({len(self.fifa_channels)})")
        
        if self.sports_channels:
            self.category_list.insert(tk.END, f"⚽ স্পোর্টস ({len(self.sports_channels)})")
        
        if self.channels:
            self.category_list.insert(tk.END, f"📺 সব চ্যানেল ({len(self.channels)})")
        
        for cat in sorted(self.categories.keys()):
            if cat not in ['🏆 FIFA World Cup', '⚽ স্পোর্টস']:
                channels = self.categories[cat]
                if channels:
                    self.category_list.insert(tk.END, f"📁 {cat} ({len(channels)})")
    
    def on_category_select(self, event):
        """ক্যাটাগরি সিলেক্ট"""
        selection = self.category_list.curselection()
        if not selection:
            return
        
        index = selection[0]
        cat_text = self.category_list.get(index)
        
        if '(' in cat_text:
            cat_name = cat_text.split('(')[0].strip()
        else:
            cat_name = cat_text.strip()
        
        channels_to_show = []
        
        if 'FIFA' in cat_name:
            channels_to_show = self.fifa_channels.copy()
        elif 'স্পোর্টস' in cat_name:
            channels_to_show = self.sports_channels.copy()
        elif 'সব চ্যানেল' in cat_name:
            channels_to_show = self.channels.copy()
        else:
            cat_clean = cat_name.replace('📁', '').strip()
            if cat_clean in self.categories:
                channels_to_show = self.categories[cat_clean].copy()
        
        self.channel_list.delete(0, tk.END)
        
        for idx, ch in enumerate(channels_to_show, 1):
            self.channel_list.insert(tk.END, f"🟢 {idx:3d}  {ch['name']}")
        
        self.ch_count_label.config(text=f"{len(channels_to_show)}টি লাইভ চ্যানেল")
    
    def search_channels(self, *args):
        """সার্চ"""
        search_term = self.search_var.get().lower()
        
        if search_term == "🔍 চ্যানেল খুঁজুন..." or search_term == "":
            self.on_category_select(None)
            return
        
        self.channel_list.delete(0, tk.END)
        
        found = [c for c in self.channels if search_term in c['name'].lower()]
        
        for idx, ch in enumerate(found, 1):
            self.channel_list.insert(tk.END, f"🟢 {idx:3d}  {ch['name']}")
        
        self.ch_count_label.config(text=f"{len(found)}টি চ্যানেল পাওয়া গেছে")
    
    def play_url(self):
        """URL পেস্ট করে প্লে"""
        url = self.url_entry.get().strip()
        
        if not url or url == "🔗 URL পেস্ট করুন...":
            messagebox.showwarning("সতর্কতা", "দয়া করে একটি URL দিন!")
            return
        
        if not url.startswith(('http', 'https')):
            messagebox.showwarning("সতর্কতা", "বৈধ URL দিন")
            return
        
        channel = {
            'name': 'লাইভ স্ট্রিম',
            'url': url,
            'working': True
        }
        
        self.play_channel(channel)
    
    def play_selected(self, event=None):
        """চ্যানেল প্লে"""
        if not self.mpv_path:
            messagebox.showerror("এরর", "MPV পাওয়া যায়নি!\n\nইনস্টল করুন: https://mpv.net/")
            return
        
        selection = self.channel_list.curselection()
        if not selection:
            return
        
        item = self.channel_list.get(selection[0])
        
        if '🟢' in item:
            parts = item.split('  ', 2)
            name = parts[2] if len(parts) > 2 else item
        else:
            name = item
        
        channel = None
        for ch in self.channels:
            if ch['name'] == name:
                channel = ch
                break
        
        if not channel:
            for ch in self.channels:
                if ch['name'] in name:
                    channel = ch
                    break
        
        if not channel:
            messagebox.showwarning("সতর্কতা", "চ্যানেল পাওয়া যায়নি!")
            return
        
        self.play_channel(channel)
    
    def play_channel(self, channel):
        """চ্যানেল প্লে"""
        self.current_channel = channel
        
        self.now_playing_video.config(text=f"▶ {channel['name']}")
        self.status_label.config(text=f"▶ {channel['name']}")
        
        # ভিডিও ডিসপ্লে আপডেট
        for widget in self.video_display.winfo_children():
            widget.destroy()
        
        video_loading = tk.Label(self.video_display, text=f"📺 {channel['name']}\n\n⏳ লাইভ লোড হচ্ছে...",
                                bg='#000000', fg=self.colors['text_light'],
                                font=('Segoe UI', 18), justify='center')
        video_loading.pack(fill='both', expand=True)
        
        threading.Thread(target=self.play_video, args=(channel['url'],), daemon=True).start()
    
    def play_video(self, url):
        """ভিডিও প্লে"""
        try:
            if self.player_process:
                self.player_process.terminate()
                self.player_process = None
            
            volume = self.video_volume.get()
            
            cmd = [
                self.mpv_path,
                '--no-border',
                '--ontop',
                '--really-quiet',
                f'--volume={volume}',
                '--cache=no',
                url
            ]
            
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            self.player_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            self.root.after(0, self.play_success)
            
        except Exception as e:
            self.root.after(0, lambda: self.show_error(str(e)))
    
    def play_success(self):
        """সফল"""
        self.is_playing = True
        self.video_play_btn.config(text="⏸")
        
        for widget in self.video_display.winfo_children():
            widget.destroy()
        
        video_playing = tk.Label(self.video_display, text="📺\n\n▶ লাইভ স্ট্রিম চলছে",
                                bg='#000000', fg=self.colors['green'],
                                font=('Segoe UI', 22), justify='center')
        video_playing.pack(fill='both', expand=True)
        
        self.status_label.config(text=f"▶ {self.current_channel['name']} - লাইভ")
    
    def show_error(self, error):
        """এরর"""
        for widget in self.video_display.winfo_children():
            widget.destroy()
        
        video_error = tk.Label(self.video_display, text="❌\n\nপ্লে করতে সমস্যা",
                              bg='#000000', fg=self.colors['red'],
                              font=('Segoe UI', 22), justify='center')
        video_error.pack(fill='both', expand=True)
        
        self.status_label.config(text=f"❌ {error}")
    
    def toggle_play(self):
        """প্লে/পজ"""
        if self.is_playing:
            if self.player_process:
                try:
                    self.player_process.terminate()
                    self.player_process = None
                    self.is_playing = False
                    self.video_play_btn.config(text="▶")
                    self.now_playing_video.config(text="⏸ পজ")
                    
                    for widget in self.video_display.winfo_children():
                        widget.destroy()
                    
                    video_paused = tk.Label(self.video_display, text="📺\n\n⏸ পজ করা হয়েছে",
                                           bg='#000000', fg=self.colors['text_muted'],
                                           font=('Segoe UI', 22), justify='center')
                    video_paused.pack(fill='both', expand=True)
                except:
                    pass
        else:
            self.play_selected()
    
    def stop_playback(self):
        """স্টপ"""
        if self.player_process:
            self.player_process.terminate()
            self.player_process = None
        
        self.is_playing = False
        self.video_play_btn.config(text="▶")
        self.now_playing_video.config(text="⏸ কিছু বাজছে না")
        self.status_label.config(text="⏹ বন্ধ")
        
        self.splash_screen()

if __name__ == "__main__":
    root = tk.Tk()
    app = RakibPersonalTV(root)
    root.mainloop()
import ctypes
import threading
import time
import queue
from ctypes import wintypes

# Windows Types
WNDPROC = ctypes.WINFUNCTYPE(wintypes.LPARAM, wintypes.HWND, wintypes.UINT, 
                              wintypes.WPARAM, wintypes.LPARAM)

class WNDCLASSEXW(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("style", ctypes.c_uint),
        ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", ctypes.c_void_p),
        ("hIcon", ctypes.c_void_p),
        ("hCursor", ctypes.c_void_p),
        ("hbrBackground", ctypes.c_void_p),
        ("lpszMenuName", ctypes.c_wchar_p),
        ("lpszClassName", ctypes.c_wchar_p),
        ("hIconSm", ctypes.c_void_p),
    ]

class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", ctypes.c_void_p),
        ("message", ctypes.c_uint),
        ("wParam", ctypes.c_ulonglong),
        ("lParam", ctypes.c_longlong),
        ("time", ctypes.c_ulong),
        ("pt_x", ctypes.c_long),
        ("pt_y", ctypes.c_long),
    ]

# Load DLLs
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
gdi32 = ctypes.windll.gdi32

# Define WinAPI functions for 64-bit compatibility
user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.DefWindowProcW.restype = wintypes.LPARAM

user32.CreateWindowExW.argtypes = [wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD, 
                                   wintypes.INT, wintypes.INT, wintypes.INT, wintypes.INT, 
                                   wintypes.HWND, wintypes.HMENU, wintypes.HANDLE, wintypes.LPVOID]
user32.CreateWindowExW.restype = wintypes.HWND

user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, ctypes.c_void_p, ctypes.c_void_p]
user32.SendMessageW.restype = ctypes.c_void_p

user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, ctypes.c_void_p, ctypes.c_void_p]
user32.PostMessageW.restype = wintypes.BOOL

user32.GetMessageW.argtypes = [ctypes.POINTER(MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
user32.GetMessageW.restype = wintypes.BOOL

user32.PeekMessageW.argtypes = [ctypes.POINTER(MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT, wintypes.UINT]
user32.PeekMessageW.restype = wintypes.BOOL

user32.DispatchMessageW.argtypes = [ctypes.POINTER(MSG)]
user32.DispatchMessageW.restype = wintypes.LPARAM

user32.TranslateMessage.argtypes = [ctypes.POINTER(MSG)]
user32.TranslateMessage.restype = wintypes.BOOL

user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
user32.GetWindowTextLengthW.restype = wintypes.INT

user32.SetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPCWSTR]
user32.SetWindowTextW.restype = wintypes.BOOL

user32.ShowWindow.argtypes = [wintypes.HWND, wintypes.INT]
user32.ShowWindow.restype = wintypes.BOOL

user32.UpdateWindow.argtypes = [wintypes.HWND]
user32.UpdateWindow.restype = wintypes.BOOL

user32.DestroyWindow.argtypes = [wintypes.HWND]
user32.DestroyWindow.restype = wintypes.BOOL

user32.RegisterClassExW.argtypes = [ctypes.c_void_p]
user32.RegisterClassExW.restype = wintypes.ATOM

user32.UnregisterClassW.argtypes = [wintypes.LPCWSTR, wintypes.HINSTANCE]
user32.UnregisterClassW.restype = wintypes.BOOL

user32.SetFocus.argtypes = [wintypes.HWND]
user32.SetFocus.restype = wintypes.HWND

user32.GetSystemMetrics.argtypes = [wintypes.INT]
user32.GetSystemMetrics.restype = wintypes.INT

gdi32.CreateFontW.argtypes = [wintypes.INT, wintypes.INT, wintypes.INT, wintypes.INT, wintypes.INT, 
                              wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, 
                              wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, 
                              wintypes.LPCWSTR]
gdi32.CreateFontW.restype = wintypes.HANDLE

gdi32.DeleteObject.argtypes = [wintypes.HANDLE]
gdi32.DeleteObject.restype = wintypes.BOOL

user32.LoadCursorW.argtypes = [wintypes.HINSTANCE, ctypes.c_void_p]
user32.LoadCursorW.restype = wintypes.HANDLE

try:
    comctl32 = ctypes.windll.comctl32
    comctl32.InitCommonControlsEx.argtypes = [ctypes.c_void_p]
    comctl32.InitCommonControlsEx.restype = wintypes.BOOL
except:
    pass

kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
kernel32.GetModuleHandleW.restype = wintypes.HINSTANCE

kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
kernel32.GlobalAlloc.restype = wintypes.HGLOBAL

kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
kernel32.GlobalLock.restype = wintypes.LPVOID

kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
kernel32.GlobalUnlock.restype = wintypes.BOOL

user32.OpenClipboard.argtypes = [wintypes.HWND]
user32.OpenClipboard.restype = wintypes.BOOL

user32.EmptyClipboard.argtypes = []
user32.EmptyClipboard.restype = wintypes.BOOL

user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
user32.SetClipboardData.restype = wintypes.HANDLE

user32.CloseClipboard.argtypes = []
user32.CloseClipboard.restype = wintypes.BOOL

# Initialize Common Controls
try:
    comctl32 = ctypes.windll.comctl32
    class INITCOMMONCONTROLSEX(ctypes.Structure):
        _fields_ = [("dwSize", ctypes.c_ulong), ("dwICC", ctypes.c_ulong)]
    icc = INITCOMMONCONTROLSEX()
    icc.dwSize = ctypes.sizeof(INITCOMMONCONTROLSEX)
    icc.dwICC = 0x00000020
    comctl32.InitCommonControlsEx(ctypes.byref(icc))
except:
    pass


class ProgressWindow:
    def __init__(self, title="Loading..."):
        self.title = title
        self.hwnd = None
        self.hwnd_progress = None
        self.hwnd_status = None
        self.hwnd_log = None
        self.hwnd_ok_btn = None
        self.is_running = False
        self.message_queue = queue.Queue()
        self.progress_queue = queue.Queue()
        self.window_thread = None
        self.log_text = ""
        self._wndproc = None
        self.hfont = None
        self._finished = False
        self._on_ok_callback = None
        
    def start(self):
        self.is_running = True
        self.log_text = ""
        self._finished = False
        self.window_thread = threading.Thread(target=self._create_window, daemon=True)
        self.window_thread.start()
        time.sleep(0.3)
        
    def _create_window(self):
        try:
            hInstance = kernel32.GetModuleHandleW(None)
            
            # Window procedure
            def wndproc(hwnd, msg, wparam, lparam):
                if msg == 0x0010:  # WM_CLOSE
                    if not self._finished:
                        return 0
                    self.is_running = False
                    user32.DestroyWindow(hwnd)
                    return 0
                elif msg == 0x0002:  # WM_DESTROY
                    self.is_running = False
                    return 0
                elif msg == 0x0111:  # WM_COMMAND
                    cmd = wparam & 0xFFFF
                    if cmd == 1001:
                        self._copy_log()
                    elif cmd == 1002:
                        if self._on_ok_callback:
                            self._on_ok_callback()
                        self.is_running = False
                        user32.DestroyWindow(hwnd)
                    return 0
                return user32.DefWindowProcW(hwnd, msg, wparam, lparam)
            
            self._wndproc = WNDPROC(wndproc)
            
            # Register class
            class_name = f"SKPProgress_{id(self)}"
            wc = WNDCLASSEXW()
            wc.cbSize = ctypes.sizeof(WNDCLASSEXW)
            wc.style = 3  # CS_HREDRAW | CS_VREDRAW
            wc.lpfnWndProc = self._wndproc
            wc.hInstance = hInstance
            wc.hCursor = user32.LoadCursorW(None, 32512)  # IDC_ARROW
            wc.hbrBackground = ctypes.c_void_p(16)  # COLOR_BTNFACE + 1
            wc.lpszClassName = class_name
            
            if not user32.RegisterClassExW(ctypes.byref(wc)):
                print("SKP | Failed to register class")
                return
            
            # Center window
            sw = user32.GetSystemMetrics(0)
            sh = user32.GetSystemMetrics(1)
            ww, wh = 600, 500
            x = (sw - ww) // 2
            y = (sh - wh) // 2
            
            # Create window with minimize button
            # WS_OVERLAPPED=0, WS_CAPTION=0xC00000, WS_SYSMENU=0x80000, WS_MINIMIZEBOX=0x20000, WS_VISIBLE=0x10000000
            self.hwnd = user32.CreateWindowExW(
                0x00040000,  # WS_EX_APPWINDOW
                class_name, self.title,
                0x10CA0000,  # WS_VISIBLE | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX
                x, y, ww, wh,
                None, None, hInstance, None
            )
            
            if not self.hwnd:
                print(f"SKP | Failed to create window: {kernel32.GetLastError()}")
                return
            
            # Font
            self.hfont = gdi32.CreateFontW(-15, 0, 0, 0, 400, 0, 0, 0, 0, 0, 0, 0, 0, "Segoe UI")
            hfont_bold = gdi32.CreateFontW(-16, 0, 0, 0, 700, 0, 0, 0, 0, 0, 0, 0, 0, "Segoe UI")
            
            # Status label
            self.hwnd_status = user32.CreateWindowExW(
                0, "STATIC", "Starting...",
                0x50000000,  # WS_CHILD | WS_VISIBLE
                20, 20, 550, 28,
                self.hwnd, None, hInstance, None
            )
            user32.SendMessageW(self.hwnd_status, 0x30, hfont_bold, 1)  # WM_SETFONT
            
            # Progress bar
            self.hwnd_progress = user32.CreateWindowExW(
                0, "msctls_progress32", None,
                0x50000001,  # WS_CHILD | WS_VISIBLE | PBS_SMOOTH
                20, 55, 550, 28,
                self.hwnd, None, hInstance, None
            )
            user32.SendMessageW(self.hwnd_progress, 0x0401, 0, 100 << 16)  # PBM_SETRANGE
            
            # Log label
            lbl = user32.CreateWindowExW(
                0, "STATIC", "Log:",
                0x50000000,
                20, 95, 550, 20,
                self.hwnd, None, hInstance, None
            )
            user32.SendMessageW(lbl, 0x30, self.hfont, 1)
            
            # Log area
            self.hwnd_log = user32.CreateWindowExW(
                0x200,  # WS_EX_CLIENTEDGE
                "EDIT", "",
                0x50200844,  # WS_CHILD | WS_VISIBLE | WS_VSCROLL | ES_MULTILINE | ES_AUTOVSCROLL | ES_READONLY
                20, 120, 550, 270,
                self.hwnd, None, hInstance, None
            )
            user32.SendMessageW(self.hwnd_log, 0x30, self.hfont, 1)
            
            # Copy button
            btn_copy = user32.CreateWindowExW(
                0, "BUTTON", "Copy Log",
                0x50000000,
                20, 405, 130, 38,
                self.hwnd, 1001, hInstance, None
            )
            user32.SendMessageW(btn_copy, 0x30, self.hfont, 1)
            
            # OK button (hidden)
            self.hwnd_ok_btn = user32.CreateWindowExW(
                0, "BUTTON", "OK",
                0x40000001,  # WS_CHILD | BS_DEFPUSHBUTTON (hidden)
                450, 405, 130, 38,
                self.hwnd, 1002, hInstance, None
            )
            user32.SendMessageW(self.hwnd_ok_btn, 0x30, self.hfont, 1)
            
            # Show window
            user32.ShowWindow(self.hwnd, 5)  # SW_SHOW
            user32.UpdateWindow(self.hwnd)
            
            # Message loop
            msg = MSG()
            while self.is_running:
                while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
                    user32.TranslateMessage(ctypes.byref(msg))
                    user32.DispatchMessageW(ctypes.byref(msg))
                self._process_queues()
                time.sleep(0.05)
            
            # Cleanup
            user32.UnregisterClassW(class_name, hInstance)
            if self.hfont:
                gdi32.DeleteObject(self.hfont)
            if hfont_bold:
                gdi32.DeleteObject(hfont_bold)
                
        except Exception as e:
            print(f"SKP | Window error: {e}")
            import traceback
            traceback.print_exc()
    
    def _process_queues(self):
        # Progress updates
        while not self.progress_queue.empty():
            try:
                progress, status = self.progress_queue.get_nowait()
                if self.hwnd_progress:
                    user32.SendMessageW(self.hwnd_progress, 0x0402, int(progress), 0)  # PBM_SETPOS
                if status and self.hwnd_status:
                    user32.SetWindowTextW(self.hwnd_status, f"({int(progress)}%) {status}")
            except:
                pass
        
        # Log updates
        while not self.message_queue.empty():
            try:
                msg = str(self.message_queue.get_nowait())
                self.log_text += msg + "\r\n"
                if self.hwnd_log:
                    user32.SetWindowTextW(self.hwnd_log, self.log_text)
                    user32.UpdateWindow(self.hwnd_log)
                    # Scroll to end: EM_SETSEL with -1, -1 then EM_SCROLLCARET
                    # 0xFFFFFFFFFFFFFFFF is -1 for 64-bit unsigned WPARAM/LPARAM
                    user32.SendMessageW(self.hwnd_log, 0x00B1, 0xFFFFFFFFFFFFFFFF, 0xFFFFFFFFFFFFFFFF)
                    user32.SendMessageW(self.hwnd_log, 0x00B7, 0, 0)  # EM_SCROLLCARET
            except Exception as e:
                print(f"SKP | Log update error: {e}")
    
    def _copy_log(self):
        try:
            if not self.log_text:
                return
            if user32.OpenClipboard(None):
                user32.EmptyClipboard()
                data = (self.log_text + "\0").encode('utf-16-le')
                h = kernel32.GlobalAlloc(0x42, len(data))
                if h:
                    p = kernel32.GlobalLock(h)
                    ctypes.memmove(p, data, len(data))
                    kernel32.GlobalUnlock(h)
                    user32.SetClipboardData(13, h)  # CF_UNICODETEXT
                user32.CloseClipboard()
        except:
            pass
    
    def update_progress(self, progress, status=None):
        if self.is_running:
            self.progress_queue.put((progress, status))
            
    def log_message(self, message):
        timestamp = time.strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"
        print(f"SKP | {entry}")
        if self.is_running:
            self.message_queue.put(entry)
    
    def show_finished(self, message="Completed!", on_ok=None):
        self._finished = True
        self._on_ok_callback = on_ok
        self.update_progress(100, f"Done: {message}")
        self.log_message("=" * 45)
        self.log_message(f"COMPLETED: {message}")
        self.log_message("=" * 45)
        if self.hwnd_ok_btn:
            user32.ShowWindow(self.hwnd_ok_btn, 5)  # SW_SHOW
            user32.SetFocus(self.hwnd_ok_btn)
            
    def close(self):
        self._finished = True
        self.is_running = False
        if self.hwnd:
            try:
                user32.PostMessageW(self.hwnd, 0x0010, 0, 0)  # WM_CLOSE
            except:
                pass


class ConfirmDialog:
    def __init__(self, title, message, show_cancel=True):
        self.title = title
        self.message = message
        self.show_cancel = show_cancel
        self._result = None
        self._wndproc = None
        self._done = threading.Event()
        
    def show(self):
        self._result = None
        self._done.clear()
        t = threading.Thread(target=self._create, daemon=True)
        t.start()
        self._done.wait(timeout=300)
        return self._result
    
    def _create(self):
        try:
            hInstance = kernel32.GetModuleHandleW(None)
            
            def wndproc(hwnd, msg, wparam, lparam):
                if msg == 0x0010:  # WM_CLOSE
                    self._result = False
                    self._done.set()
                    user32.DestroyWindow(hwnd)
                    return 0
                elif msg == 0x0002:  # WM_DESTROY
                    user32.PostQuitMessage(0)
                    return 0
                elif msg == 0x0111:  # WM_COMMAND
                    cmd = wparam & 0xFFFF
                    if cmd == 1:
                        self._result = True
                        self._done.set()
                        user32.DestroyWindow(hwnd)
                    elif cmd == 2:
                        self._result = False
                        self._done.set()
                        user32.DestroyWindow(hwnd)
                    return 0
                return user32.DefWindowProcW(hwnd, msg, wparam, lparam)
            
            self._wndproc = WNDPROC(wndproc)
            
            class_name = f"SKPConfirm_{id(self)}"
            wc = WNDCLASSEXW()
            wc.cbSize = ctypes.sizeof(WNDCLASSEXW)
            wc.style = 3
            wc.lpfnWndProc = self._wndproc
            wc.hInstance = hInstance
            wc.hCursor = user32.LoadCursorW(None, 32512)
            wc.hbrBackground = ctypes.c_void_p(16)
            wc.lpszClassName = class_name
            user32.RegisterClassExW(ctypes.byref(wc))
            
            sw = user32.GetSystemMetrics(0)
            sh = user32.GetSystemMetrics(1)
            ww, wh = 450, 180
            
            hwnd = user32.CreateWindowExW(
                0x00000008,  # WS_EX_TOPMOST
                class_name, self.title,
                0x10C80000,  # WS_VISIBLE | WS_CAPTION | WS_SYSMENU
                (sw-ww)//2, (sh-wh)//2, ww, wh,
                None, None, hInstance, None
            )
            
            hfont = gdi32.CreateFontW(-15, 0, 0, 0, 400, 0, 0, 0, 0, 0, 0, 0, 0, "Segoe UI")
            
            # Message
            lbl = user32.CreateWindowExW(
                0, "STATIC", self.message,
                0x50000000,
                25, 20, 390, 70,
                hwnd, None, hInstance, None
            )
            user32.SendMessageW(lbl, 0x30, hfont, 1)
            
            # OK button
            bx = 130 if self.show_cancel else 175
            btn_ok = user32.CreateWindowExW(
                0, "BUTTON", "OK",
                0x50000001,  # WS_CHILD | WS_VISIBLE | BS_DEFPUSHBUTTON
                bx, 100, 100, 35,
                hwnd, 1, hInstance, None
            )
            user32.SendMessageW(btn_ok, 0x30, hfont, 1)
            
            # Cancel button
            if self.show_cancel:
                btn_cancel = user32.CreateWindowExW(
                    0, "BUTTON", "Cancel",
                    0x50000000,
                    240, 100, 100, 35,
                    hwnd, 2, hInstance, None
                )
                user32.SendMessageW(btn_cancel, 0x30, hfont, 1)
            
            user32.SetFocus(btn_ok)
            
            msg = MSG()
            while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
            
            user32.UnregisterClassW(class_name, hInstance)
            gdi32.DeleteObject(hfont)
            
        except Exception as e:
            print(f"SKP | Dialog error: {e}")
            self._result = False
            self._done.set()


# Global functions
_current_window = None

def start_import_progress():
    global _current_window
    if _current_window:
        _current_window.close()
        time.sleep(0.1)
    _current_window = ProgressWindow("SketchUp Import")
    _current_window.start()
    return _current_window

def start_setup_progress(total_steps=10):
    global _current_window
    if _current_window:
        _current_window.close()
        time.sleep(0.1)
    _current_window = ProgressWindow("File Setup")
    _current_window.start()
    return _current_window

def get_current_progress():
    global _current_window
    return _current_window

def close_progress():
    global _current_window
    if _current_window:
        _current_window.close()
        _current_window = None

def show_confirm(title, message, show_cancel=True):
    return ConfirmDialog(title, message, show_cancel).show()

def show_message(title, message):
    return ConfirmDialog(title, message, show_cancel=False).show()

def show_finished_in_progress(message="Completed!"):
    global _current_window
    if _current_window:
        _current_window.show_finished(message)

def register():
    pass

def unregister():
    close_progress()

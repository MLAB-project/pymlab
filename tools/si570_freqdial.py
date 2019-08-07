import wx
import wx.lib.newevent
import threading

class FreqDialWidget(wx.Window):
    RedrawReqEvent, EVT_REDRAW_REQ = wx.lib.newevent.NewCommandEvent()
    NDIGITS = 7
    MAX_VALUE = 9999999
    DARK_GREY = wx.Colour(64, 64, 64)

    @classmethod
    def clamp(self, v, lo, hi):
        if v < lo:
            return lo
        if v > hi:
            return hi
        return v

    def __init__(self, parent, default=0):
        wx.Window.__init__(self, parent, size=(440, 80))

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_MOTION, self.on_mouse_moved)
        self.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel_moved)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_pressed)
        self.Bind(self.EVT_REDRAW_REQ, self.on_redraw_req)

        self.mouse_pos = wx.Point(0, 0)
        self.focused_digit_no = -1

        self.w, self.h = self.GetSize()

        self._value = default
        self._value_cv = threading.Condition()
        self._locked = False
        self._error = False

        self.fonts = [
            wx.Font(size, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL,
                    wx.FONTWEIGHT_NORMAL)
            for size in (40, 20, 12)
        ]

        dc = wx.ClientDC(self)
        dc.SetFont(self.fonts[0])
        self.border = 10
        self.digitw, self.digith = dc.GetTextExtent("0")

        border, dw = self.border, self.digitw
        self.digit_rects = [
            wx.Rect(border + dw*(8-i) - offset, border, dw, self.digith)
            for i, offset in enumerate([0, 0, 0, dw/2, dw/2, dw/2, dw])
        ]

        dc.SetFont(self.fonts[1])
        ulabelw, ulabelh = dc.GetTextExtent("kHz")
        self.khz_label_pos = (border + dw*9 + 5, border + 24)
        self.flag_label_pos = (border + dw*9 + ulabelw + 10, border + 15)

    def on_redraw_req(self, event):
        self.Refresh(); self.Update()

    @property
    def value(self):
        return self._value

    def set_flags(self, locked, error):
        if self._locked == locked and self._error == error:
            return
        self._locked, self._error = locked, error
        wx.PostEvent(self, self.RedrawReqEvent(0))

    def _set_value(self, value):
        with self._value_cv:
            if self._value == value:
                return
            self._value = value
            self._value_cv.notify_all()
        self.Refresh(); self.Update()

    def add_to_value(self, delta):
        self._set_value(self.clamp(self._value + delta, 0, self.MAX_VALUE))

    def on_paint(self, event):
        dc = wx.PaintDC(self)

        dc.SetBrush(wx.BLACK_BRUSH)
        dc.DrawRectangle(0, 0, self.w, self.h)

        dc.SetTextForeground(wx.WHITE)
        dc.SetFont(self.fonts[0])

        v = int(self.value)
        self.focused_digit_no = -1

        for i, rect in enumerate(self.digit_rects):
            if rect.Contains(self.mouse_pos):
                self.focused_digit_no = i
                dc.SetBrush(wx.LIGHT_GREY_BRUSH)
                dc.DrawRectangleRect(rect)

            if v != 0 or i == 0:
                dc.DrawText(str(v % 10), rect.GetX(), rect.GetY())
            v = v // 10

        dc.SetFont(self.fonts[1])
        dc.SetTextForeground(wx.LIGHT_GREY)
        dc.DrawText("kHz", *self.khz_label_pos)

        dc.SetFont(self.fonts[2])
        if self._locked:
            dc.SetTextForeground(wx.GREEN)
        else:
            dc.SetTextForeground(self.DARK_GREY)

        flag_x, flag_y = self.flag_label_pos
        dc.DrawText("LOCKED", flag_x, flag_y)

        if self._error:
            dc.SetTextForeground(wx.RED)
        else:
            dc.SetTextForeground(self.DARK_GREY)
        dc.DrawText("ERROR", flag_x, flag_y + 20)

    def on_mouse_moved(self, event):
        self.mouse_pos = event.GetPosition()
        self.Refresh(); self.Update();

    def on_mouse_wheel_moved(self, event):
        if self.focused_digit_no != -1:
            dir_ = 1 if (event.GetWheelRotation() > 0) else -1
            self.add_to_value(dir_ * 10**self.focused_digit_no)

    def move_mouse_to_digit(self, digit_no):
        dc = wx.ClientDC(self)
        rect = self.digit_rects[digit_no]
        x, y = rect.GetX()+rect.GetWidth()/2, rect.GetY()+rect.GetHeight()/2
        self.WarpPointer(dc.LogicalToDeviceX(x),
                         dc.LogicalToDeviceY(y))

    def shift_focus(self, dir_):
        assert dir_ in (1, -1)
        if self.focused_digit_no == -1:
            return
        self.move_mouse_to_digit(self.clamp(self.focused_digit_no + dir_,
                                            0, self.NDIGITS-1))

    def on_key_pressed(self, event):
        if self.focused_digit_no == -1:
            return
        key = event.GetKeyCode()
        if key in [wx.WXK_LEFT, wx.WXK_RIGHT]:
            self.shift_focus(1 if key == wx.WXK_LEFT else -1)
        if key in [wx.WXK_UP, wx.WXK_DOWN]:
            dir_ = 1 if key == wx.WXK_UP else -1
            self.add_to_value(dir_ * 10**self.focused_digit_no)
        if key in range(48, 58):
            num = key - 48
            focused = 10**self.focused_digit_no
            new_val = self._value - (self._value // focused % 10) * focused
            new_val += focused * num
            self._set_value(new_val)
            self.shift_focus(-1)

app = wx.App()
top = wx.Frame(None, title="Frequency Dial")
sizer = wx.BoxSizer(wx.VERTICAL)

dial = FreqDialWidget(top, default=10e3)
sizer.AddF(dial, wx.SizerFlags().Expand().Border())

import time
def thread():
    from pymlab import config
    import sys

    if len(sys.argv) != 2:
            sys.stderr.write("Invalid number of arguments. Missing path to a config file!\n")
            sys.stderr.write("Usage: %s i2c_bus.cfg\n" % (sys.argv[0], ))
            sys.exit(1)

    cfg = config.Config()
    cfg.load_file(sys.argv[1])
    cfg.initialize()
    fgen = cfg.get_device("clkgen")
    fgen.route()
    fgen.recall_nvm()

    set_ = 1
    si570_freq = 10.0

    error = False
    while True:
        with dial._value_cv:
            if set_ == dial._value:
                dial.set_flags(not error, error)
                dial._value_cv.wait()
                dial.set_flags(False, False)
        set_ = dial.value
        freq_mhz = float(set_) / 1e3
        try:
            fgen.set_freq(si570_freq, freq_mhz)
            si570_freq = freq_mhz
        except Exception:
            try:
                fgen.recall_nvm()
                fgen.set_freq(10.0, freq_mhz)
                si570_freq = freq_mhz
            except Exception:
                error = True
            else:
                error = False
        else:
            error = False

t = threading.Thread(target=thread)
t.start()

top.SetMinSize(wx.Size(440, 120))
top.SetMaxSize(wx.Size(440, 120))
top.SetSizer(sizer)
top.Layout()
top.Fit()
top.Show()
app.MainLoop()

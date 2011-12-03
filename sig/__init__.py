import cPickle,array,heapq

import numpy,scipy.signal


def memoize(func):
    """
    this is a decorator used to memoize an instance method's output.

    note that this assumes:

        (1) that it is decorating an instance mehtod
        (2) that the arguments to the decorated method (minus the 'self') are
        hashable if put into a tuple.

    usage:
        @memoize
        def blah(self, arg1, arg2):
            '''this will only run once'''
            return some_lengthy_calculation(arg1, arg2)

    """
    def _get(self, *args):
        cache_name = '_' + func.__name__ + '_cache'
        if not hasattr(self, cache_name):
            setattr(self, cache_name, {})
        cache = getattr(self, cache_name)

        key = tuple(args)
        if key not in cache:
            cache[key] = func(self, *args)

        return cache[key]

    return _get

def cached_property(func, name=None):
    """
    this decorator creates a cached property of an instance attribute.
    
    usage:
        @cached_property
        def blah(self):
            '''this will only run once'''
            return some_lengthy_calculation()

    the property can only be gotten, no set/delete methods are defined by this
    decorator
    """
    if name is None :
        name = '_' + func.__name__ 

    def _get(self):
        if not hasattr(self, name):
            setattr(self, name, func(self))
        return getattr(self, name)

    return property(_get)

def smooth(x,window_len=11,window='hanning'):
    """
    smooth the data using a window with requested size.

    from here:

        http://www.scipy.org/Cookbook/SignalSmooth
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal (with
    the window size) in both ends so that transient parts are minimized in the
    begining and end part of the output signal.
    
    input:
        x: 
            the input signal 
        window_len:
            the dimension of the smoothing window; should be an odd integer
        window:
            the type of window from 'flat', 'hanning', 'hamming', 'bartlett',
            'blackman' flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:
        t=linspace(-2,2,0.1)
        x=sin(t)+randn(len(t))*0.1
        y=smooth(x)
    
    see also: 
        numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman,
        numpy.convolve, scipy.signal.lfilter
    """

    if x.ndim != 1:
        raise ValueError('smooth only accepts 1 dimension arrays.')

    if x.size < window_len:
        raise ValueError('Input vector needs to be bigger than window size.')


    if window_len<3:
        return x


    allowed_types = ('flat', 'hanning', 'hamming', 'bartlett', 'blackman')
    if not window in allowed_types:
        raise ValueError('"window" must be one of %s' % \
                ', '.join(t for t in allowed_types))


    s=numpy.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
    if window == 'flat': #moving average
        w=numpy.ones(window_len,'d')
    else:
        w=eval('numpy.'+window+'(window_len)')

    y=numpy.convolve(w/w.sum(),s,mode='valid')
    return y

def local_extrema(s, combined=False):
    """
    return two lists, one of local mins, one of local maxes
    """
    increasing = None
    for j,v in enumerate(s[1:], 1):
        if v > s[j-1]:
            increasing = True
            break
        elif v < s[j-1]:
            increasing = False
            break

    if increasing == None:
        # we never saw any peaks, return empty output
        return [] if combined else ([], [])

    last = s[j-1]
    mins, maxs = [], []
    for i in xrange(j, len(s)):
        if increasing:
            if s[i] < s[i-1]:
                mins.append(i-1)
                increasing = False
        else:
            if s[i] > s[i-1]:
                maxs.append(i-1)
                increasing = True

    return sorted(mins + maxs) if combined else (mins, maxs)

def raw_signal(fname):
    """
    convenience function to get a raw signal as an arra.array() from a PCM file

    "fname" is the filename of the signal in S16LE PCM format
    """
    a = array.array('h')
    a.fromstring(open(fname).read())
    return a

class Signal(object):

    # sampling frequency
    FS = 44100.0

    # the size of the window used to check whether we've reached the end of the
    # signal
    END_WIN_LEN = 90                                

    # this is the threshold for deciding the signal has ended.  if the average
    # of the abs value of the amplitude of the last END_WIN_LEN samples dips
    # below this, we've reached the end of the signal
    LOW_AVERAGE = 200.

    # the amplitude that triggers the start of the signal
    START_THRESHOLD = 400.

    # the window size used in finding the start of the signal
    START_WINDOW_SIZE = 0.1

    # the number of peaks in the start window to comapre to the average
    START_WINDOW_NUM_PEAKS = 10

    # the minimum number of samples between peaks
    MIN_SEPARATION = 10

    # the minimum difference in amplitude from one peak to the next
    GATE = 50

    # the minimum length of time of a swipe (units in seconds)
    MIN_SWIPE_LEN = 0.2

    def __init__(self, raw_signal=[]):
        self.raw_signal = raw_signal;

    @cached_property
    def x(self):
        return numpy.arange(len(self.y)) / self.FS

    @cached_property
    def y(self):
        return numpy.array([ float(i) for i in self.raw_signal ])

    @cached_property
    def abs_y(self):
        return abs(self.y)

    def _find_start_and_end(self):
        """
        i was just doing a dumb start threshold.  this wasn't very robust, so i
        came up w/ a much more complicated method that takes a window, compares
        the 10 higest values to the average, and then looks for 10 consecutive
        windows of a large difference between these two values.

        turns out this isn't much more robust.  but it works for the data
        coming from the phone, so oh well.
        """
        l = self.START_WINDOW_SIZE * self.FS
        n = self.START_WINDOW_NUM_PEAKS
        rng = range(0, len(self.abs_y), int(l / 4))
        self._start_prop = 0

        avgs = numpy.zeros(len(rng))
        above_10_count = 0
        above_10_start = None
        for ii,i in enumerate(rng):
            avg = sum(self.abs_y[i:i+l]) / l
            peaks = heapq.nlargest(n, self.abs_y[i:i+l])
            peak_avg = sum(peaks) / n
            avgs[ii] = peak_avg - avg
            if peak_avg - avg >= 10:
                above_10_count += 1
                if above_10_count == 10:
                    above_10_start = rng[ii - 9]
                    above_10_value = avgs[ii - 9]
            else:
                above_10_count = 0

        for i,v in enumerate(self.y[above_10_start:], above_10_start):
            if v > (above_10_value / 2.0):
                self._start_prop = i
                break

        # while we've figured all this stuff out, go ahead and save off the end
        # index
        above_10_end = above_10_start / int(l / 4)
        while avgs[above_10_end] > 5:
            above_10_end += 1

        self._end_prop = above_10_end * int(l / 4)

    @cached_property
    def start(self):
        if not hasattr(self, '_start_prop'):
            self._find_start_and_end()
        return self._start_prop
    start_time = cached_property(lambda self: self.start/self.FS)

    @cached_property
    def end(self):
        if not hasattr(self, '_end_prop'):
            self._find_start_and_end()
        return self._end_prop
    @cached_property
    def end_time(self):
        return self.end/self.FS

    @memoize
    def smoothed(self, window_len=None):
        if type(window_len) == int:
            smoothed_sig = smooth(self.y, window_len=window_len)

            # smoothing may return something longer than the original signal.
            # if it did then cut the ends off the smoothed signal
            if len(self.y) != len(smoothed_sig):
                diff = len(self.y) - len(smoothed_sig)
                start = abs(diff) / 2
                end = abs(diff) - start
                return smoothed_sig[start:-end]
            else:
                return smoothed_sig
        else:
            # 'smoothing' parameter was None, so just return the signal
            return self.y

    @memoize
    def medfilt(self, window_len=7, smoothing=None):
        return scipy.signal.medfilt(self.smoothed(smoothing), window_len)

    @memoize
    def peaks(self, window_len=7, smoothing=10):
        return self.smoothed(smoothing) - self.medfilt(window_len, smoothing)

    @memoize
    def hist_threshold_filtered(self, extra=0.5, hist_win_size=200):
        """
        we need to get a cutoff amplitude for the (medfilt-signal) curve.  the
        prob is this cutoff changes.

        this will create a histogram, which allows me to find the cutoff
        threshold based on the local minimum of the histogram curve

        hist_win_size: is the range of the histogram bucket

        extra: this is diffucult to explain.  background: this function uses
        the histogram to determine the cutoff for peaks.  all values below the
        cutoff are zeroed out.  usually it is best if the cutoff is bumped up
        by about 1/2 a histogram window size.  this is the parameter to set
        that
        """
        tot_len = self.end - self.start
        htf = self.peaks().copy()

        for i in range(self.start, self.end, hist_win_size):
            hist, bin_edges = numpy.histogram(self.peaks()[i:i+hist_win_size])
            cutoff = abs(bin_edges[local_extrema(hist)[0][0] + 2])
            cutoff += extra * hist_win_size

            for j in range(i, i + hist_win_size):
                if abs(htf[j]) <= cutoff:
                    htf[j] = 0
        return htf

class Decoder(object):

    def __init__(self, signal, filtering='medfilt'):
        self.s = signal
        self.sig = \
                self.s.y if filtering == None else getattr(self.s, filtering)()

    def next_peak(self, idx, limit=None):
        """
        this returns the index of the next peak after 'idx', or None if it does
        not find one before 'limit'. if 'limit' is none, it will search to the
        end of the signal
        """
        increasing = True if self.sig[idx+1] > self.sig[idx] else False

        for i,v in enumerate(self.sig[idx+1:], start=idx+1):
            if  v > self.sig[i-1] and not increasing or \
                v < self.sig[i-1] and increasing:
                return i-1

        return None

    def get_start_idx_and_period(self, consecutive_periods=6):
        """
        this picks a good starting point where the signal has been established
        and returns the index of that peak and the list of periods up to that
        peak

        start: the index to start looking for peaks.  defaults to the 'start'
        attribute of the Signal class

        consecutive_periods: the number of good consecutive periods to find
        before returning.

        a good consecutive period is one whose width is within 80% of the
        preceding periods.
        """
        for start,v in enumerate(self.sig[self.s.start:], self.s.start):
            if abs(v) > 10:
                break

        cur = self.next_peak(start)
        periods = [cur - start]
        last = start
        count = 0
        while True:
            last = cur
            cur = self.next_peak(cur)
            avg = sum(periods)/len(periods)
            if abs((cur - last) - avg) > 0.8 * avg:
                periods = [cur - last]
            else:
                periods.insert(0, cur - last)
                if len(periods) >= consecutive_periods:
                    start = cur
                    break

        return start, periods

    def disaster_recovery(self, cur_idx, period):
        """
        this function assumes that there was no local extrema found in the
        expected window for the get_digit function.
        
        so this is going to be my algorithm:

        - consider the middle 40% of the window
        - if there are no local extrema in this sub-window, it is a zero
        - otherwise it's a one
        - either way return a tuple: (index, magnitude)
        - if it's a 1, the magnitude will be the same as cur_idx
        - if it's a 0, the magnitude will be the opposite of cur_idx
        """
        win_start, win_end = (int(cur_idx + 0.30*period),
                              int(cur_idx + 0.70*period))

        if len(local_extrema(self.sig[win_start:win_end], combined=True)) == 0:
            bit = 0  # becuse there are no local extrema in the sub-window
            mag = -1 * self.sig[cur_idx]
        else:
            bit = 1  # becuse there are local extrema in the sub-window
            mag =      self.sig[cur_idx]

        return mag, cur_idx + period, {
                'cur_idx': cur_idx,
                'period': period,
                'bit': bit,
            }

    def get_end_idx(self):
        cur = self.s.end
        while self.sig[cur] < 10:
            cur -= 1
        return cur

    def bits(self):
        cur_idx, periods = self.get_start_idx_and_period()
        end_idx = self.get_end_idx()
        period = sum(periods) / len(periods)
        error = None

        while cur_idx + period < end_idx:
            win_start = int(cur_idx + period - 0.30*period)
            win_end   = int(cur_idx + period + 0.30*period)

            cur_val = self.sig[cur_idx] if error == None else largest_val

            le = local_extrema(self.sig[win_start:win_end], combined=True)
            if len(le) == 0:
                largest_val, idx_of_largest, error = \
                        self.disaster_recovery(cur_idx, period)
                largest_mag = abs(largest_val)
            else:
                extrema = [ (win_start+e, self.sig[win_start + e]) for e in le ]
                largest_mag, idx_of_largest = \
                        max( (abs(y), x) for x, y in extrema )
                largest_val = self.sig[idx_of_largest]
                error = None

            polarity_was_reversed = max(largest_mag, abs(cur_val)) < \
                                    abs(cur_val - largest_val)
            bit = 0 if polarity_was_reversed else 1

            yield bit, cur_idx, periods, error

            periods.insert(0, idx_of_largest - cur_idx)
            periods.pop()
            cur_idx = idx_of_largest
            period = sum(periods) / len(periods)

class ParityError(Exception): pass
class ParseError(Exception): pass

def get_digit(ss):
    errs = []

    if len(ss) < 5:
        errs.append(ParseError('string len must be > 5: %s' % ss))
    if int(ss[4]) != (ss[:4].count('1') + 1) % 2:
        errs.append(ParityError('digit parity error: %s' % ss[:5]))

    d = 0
    for i,c in enumerate(ss[:4]):
        d |= (int(c) << i)

    return d, errs

START_SENTINEL = '11010'
END_SENTINEL = '11111'
FIELD_SEPARATOR = '10110'

def cc_num(s, start_sentinel=START_SENTINEL, field_separator=FIELD_SEPARATOR,
        end_sentinel=END_SENTINEL):
    """
    parse a bit string into a credit card number.

    s:      this is either a string or a generator of bits (as strings or ints)

    """
    errs = []
    chrs = []

    if hasattr(s, 'next'):
        s = ''.join([ str(i) for i in s ])

    charW = len(start_sentinel)

    start_idx = s.find(start_sentinel)
    cur_idx = start_idx
    if cur_idx > len(s) - charW:
        errs.append(ParseError('no start sentinel'))
    end_idx = s.rfind(end_sentinel)

    while cur_idx + charW <= len(s):
        d = 0
        count = 0
        for i in xrange(charW - 1):
            v = int(s[cur_idx+i])
            count += v
            d |= int(s[cur_idx+i]) << i
        parity_bit = int(s[cur_idx + charW - 1])

        if (count + 1) % 2 != parity_bit:
            err = 'digit parity error: \n%s\n%s' % \
                    (s[start_idx:end_idx+charW],
                     ' '*(cur_idx - start_idx) + s[cur_idx:cur_idx+charW])
            errs.append(ParityError(err))

        if cur_idx <= end_idx:
            yield chr(d + 48)
        else:
            break

        cur_idx += charW

    lrc, lrc_errs = calc_lrc(s)
    errs += lrc_errs
    if d != lrc:
        errs.append(ParityError('bitstring parity error: received %d' % d))

def calc_lrc(bitstring, start_sentinel=START_SENTINEL,
        end_sentinel=END_SENTINEL):

    errs = []

    for i in range(len(bitstring)):
        if bitstring[i:i+5] == start_sentinel: break
    start = i

    for i in range(0, len(bitstring[start:]), 5):
        if bitstring[start+i:start+i+5] == end_sentinel:
            break
    else:
        errs.append(
            ParseError('no end sentinel found while calculating parity'))

    end = start + i + 5

    s = bitstring[start:end]

    if len(s) % 5 != 0:
        errs.append(ParseError('incomplete digits found while calculating lrc'))
        return -1, errs

    digits = []
    i = 0
    while i < len(s):
        digits.append(s[i:i+5])
        i += 5

    lrc = ''.join(
            [str(sum(int(d[i]) for d in digits).__mod__(2)) for i in range(5)])

    d, digit_errs = get_digit(lrc)
    errs += digit_errs
    return d, errs

from rum.matchers import require_all, require_any
from rum.midi import MidiMessage


class MidiProcessor:
    """ Processor whose sole function is to dispatch midi messages.

    MidiProcessor is a convenience structure that receives a single midi message
    and dispatches it to multiple end points. These dispatch functions can
    have built-in conditions that drop or transmit the message to its end point.
    """
    def __init__(self):
        self._processors = []

    def add(self, *var_processor_fns):
        """ Add processor function to trigger when a midi message is processed.

        This method accepts a variable number of arguments. The functions are
        triggered in the order they are added and provided. Each function
        will be passed a single argument of type MidiMessage. This message is
        mutable and changes to it will be propagated to the later processing
        functions. The MidiMessage can be marked handled by modifying the
        handled field. This prevents further processing by FL Studio (e.g.
        sound generation).

        :param var_processor_fns: a variable list of processor functions to
        call when a midi message is input. A processor function takes a single
        input argument of type MidiMessage. The functions are called in the
        order they are provided and added.
        :return: this instance for further operation chaining
        """
        for fn in var_processor_fns:
            self._processors.append(fn)
        return self

    def clear(self):
        """ Clears all processors. """
        self._processors.clear()

    def process(self, message: MidiMessage):
        """ Process midi message by sending it to all processor functions. """
        for p in self._processors:
            p(message)
        return self


_active_processor = MidiProcessor()


def get_processor():
    """ Returns the singleton processor. """
    return _active_processor


class When:
    """ Factory for converting a matcher function into a process function.

    A matcher function takes an input MidiMessage and returns a boolean
    specifying whether some conditional function on the input matches.

    A process function takes an input MidiMessage, and executes something
    based on the midi message.

    This class combines a matcher and processor so that it becomes an if-then
    processor function. To be fluent, use the

    e.g.
       process_fn = When(status_eq(128)).then(trigger_fn)
       ...
       process_fn(msg)   # Calls trigger_fn(msg) if msg.status == 128
    """
    def __init__(self, matcher_fn):
        self._matcher_fn = matcher_fn

    def then(self, *var_trigger_fn):
        """ Action to execute """
        def process_fn(msg):
            if self._matcher_fn(msg):
                for trigger_fn in var_trigger_fn:
                    trigger_fn(msg)

        return process_fn


class WhenAll(When):
    """ Similar to When but requires all input matchers to be True. """
    def __init__(self, *var_matcher_fns):
        super().__init__(require_all(*var_matcher_fns))


class WhenAny(When):
    """ Similar to When but requires any input matchers to be True. """
    def __init__(self, *var_matcher_fns):
        super().__init__(require_any(*var_matcher_fns))


# Convenience syntax. Allow lower-case function method call.
# Have when(...)  with multiple args default to WhenAll.

when = WhenAll
when_all = WhenAll
when_any = WhenAny

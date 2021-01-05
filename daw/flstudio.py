""" All bindings to FL Studio dependent APIs will go here.

To simplify the programming concept, we break down the concept of FL Studio
into several independent components. These components can be controlled by
a dedicated device or device attached to controlling these device based on mode
changes.

The concepts are as follows:

- ChannelRack: This is the place users go to select the active instrument to
play, tweak the generated sound parameters (e.g. plugin params).
- MixerPanel: This is the place users go to tweak the volume/spatial levels of
different channels. This also includes mixer effects and routing information.
- TransportPanel: The transport panel is responsible for play/stop/record and
position of the song during recording/playback.
- PatternPanel: This is the place users go to switch to different pattern tracks
for recording. Users can also arrange/edit overall recorded patterns.

Buttons and controls can dynamically attach/detach from these individual
components.
"""

import channels
import device

from rum.midi import MidiMessage


class ChannelRack:
    """ Methods in FL Studio for controlling the channel rack. """
    @staticmethod
    def active_channel():
        """ Returns the first selected channel """
        return channels.selectedChannel()

    @staticmethod
    def num_channels():
        return channels.channelCount()

    @staticmethod
    def name(index):
        return channels.getChannelName(index)

    @staticmethod
    def set_active_channel(index):
        channels.selectOneChannel(index)

    @staticmethod
    def play_midi_note(channel, note, velocity):
        channels.midiNoteOn(channel, note, velocity)


class Midi:
    @staticmethod
    def to_midi_message(event: 'eventData'):
        """ Convert an FL Studio eventData midi message to MidiMessage. """
        return MidiMessage(event.status, event.data1, event.data2)


class Device:
    @staticmethod
    def send_sysex_message(byte_str):
        """ Send a midi SYSEX message to the linked output device. """
        return device.midiOutSysex(byte_str)

    @staticmethod
    def get_port_number():
        """ Fetches the MIDI port number assigned to this device. """
        return device.getPortNumber()

    @staticmethod
    def dispatch_message_to_other_scripts(status, data1, data2):
        """ Dispatches the midi note to all other scripts. """
        for i in range(device.dispatchReceiverCount()):
            msg = status + (data1 << 8) + (data2 << 16)
            device.dispatch(i, msg)

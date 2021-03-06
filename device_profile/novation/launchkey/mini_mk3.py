from device_profile.abstract import MidiCommandBuilder, DeviceProfile
from rum import displays
from rum.matchers import midi_has


class MiniMk3:
    # Reference:
    # https://www.kraftmusic.com/media/ownersmanual/Novation_Launchkey_Programmers_Reference_Manual.pdf
    CMD_PREAMBLE = bytes([
        0x9F, 0x0C, 0x00,   # Exit DAW mode (defaults to drum layout
    ])

    SOLID_LED_STATUS_CMD = 0x99
    BLINK_LED_STATUS_CMD = 0x9B

    # Button constants
    # NOTE: You could very well enable DAW mode, switch buttons over to session
    # layout and use the 0x60-0x67, 0x70-0x77 ids.
    #
    # Novation seems to maintain a separate light state for different layouts
    # so you could technically use these as animation buffers or make changes
    # to different settings without needing to worry what mode is being
    # displayed. For our simple case, we will just use the drum layout which
    # is the default layout when the keyboard is first powered on.
    DRUM_PAD_IDS = [[0x28, 0x29, 0x2A, 0x2B, 0x30, 0x31, 0x32, 0x33],
                    [0x24, 0x25, 0x26, 0x27, 0x2C, 0x2D, 0x2E, 0x2F]]

    # Mapping of the channel index the buttons map to.
    CHANNEL_MAP = {pad_id: idx for idx, pad_id in
                   enumerate(DRUM_PAD_IDS[0] + DRUM_PAD_IDS[1])}

    DRUM_PAD_MIDI_CHANNEL = 9   # corresponds to channel 10

    # Various matchers
    IS_RECORD_BUTTON = midi_has(status_range=(0xB0, 0xBF), data1=0x75)
    IS_PLAY_BUTTON = midi_has(status_range=(0xB0, 0xBF), data1=0x73)
    IS_PAGE_UP_BUTTON = midi_has(status_range=(0xB0, 0xBF), data1=0x68)
    IS_PAGE_DOWN_BUTTON = midi_has(status_range=(0xB0, 0xBF), data1=0x69)
    IS_DRUM_PAD = midi_has(status_in=[0x89, 0x99], data1_range=(0x24, 0x33))

    DRUM_PAD_DOWN_MATCHERS = [
        [midi_has(status=0x99, data1=pad_id) for pad_id in row_ids]
        for row_ids in DRUM_PAD_IDS
    ]

    DRUM_PAD_UP_MATCHERS = [
        [midi_has(status=0x89, data1=pad_id) for pad_id in row_ids]
        for row_ids in DRUM_PAD_IDS
    ]

    # Data1 codes for the encoder.
    ENCODER_IDS = [0x15, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x1B, 0x1C]
    ENCODER_MAP = {eid: idx for idx, eid in enumerate(ENCODER_IDS)}
    ENCODER_MATCHERS = [midi_has(status_range=(0xB0, 0xBF), data1=enc_id)
                        for enc_id in ENCODER_IDS]

    @staticmethod
    def is_encoder(idx):
        """ Returns a matcher that matches to the specified encoder index. """
        return MiniMk3.ENCODER_MATCHERS[idx]


class MiniMk3MidiCommandBuilder(MidiCommandBuilder):
    """ MIDI Command structure for Novation MiniMk3MidiCommandBuilder. """
    @staticmethod
    def new_command():
        return MiniMk3MidiCommandBuilder()

    def __init__(self):
        super().__init__()
        self.param_lights_to_blink = []

    def blinking_light(self, *led_id_color_args):
        """ Set the lights on the device to blink a given color. """
        assert len(led_id_color_args) % 2 == 0
        for i in range(0, len(led_id_color_args), 2):
            self.param_lights_to_blink.append(
                (led_id_color_args[i], led_id_color_args[i + 1]))
        return self

    def build(self, daw_mode=True):
        # Start with the lights
        cmd = bytes()
        if (self.param_lights_to_turn_off
                or self.param_lights_to_turn_on
                or self.param_lights_to_set_colors
                or self.param_lights_to_blink):

            if daw_mode:
                # If not in DAW mode, don't prepend the command pre-amble
                cmd += MiniMk3.CMD_PREAMBLE

            for led_id in self.param_lights_to_turn_off:
                cmd += bytes([MiniMk3.SOLID_LED_STATUS_CMD,
                              led_id,
                              0x00])

            for led_id in self.param_lights_to_turn_on:
                cmd += bytes([MiniMk3.SOLID_LED_STATUS_CMD,
                              led_id,
                              0x77])

            for led_id, led_value in self.param_lights_to_set_colors:
                cmd += bytes([MiniMk3.SOLID_LED_STATUS_CMD,
                              led_id,
                              led_value])

            for led_id, led_value in self.param_lights_to_blink:
                cmd += bytes([MiniMk3.BLINK_LED_STATUS_CMD,
                              led_id,
                              led_value])

        if self.param_display_updates:
            # No display on the Launchkey mini mk3
            pass
        return cmd


class MiniMk3DeviceProfile(DeviceProfile):
    def new_midi_command_builder(self):
        return MiniMk3MidiCommandBuilder()

    def new_display(self, daw_mode=True):
        # No-op displays since no displays exists.
        return displays.DirectDisplay(0, 0)

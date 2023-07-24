import logging
import datetime
import json
import os
import io
import time
import requests

def file_logger(log_path):
    logger = logging.getLogger('xml_logger')
    logger.setLevel(logging.DEBUG)
    os.makedirs(log_path, exist_ok=True)
    log_file = f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.log'
    log_file = os.path.join(log_path, log_file)
    fh = logging.FileHandler(filename=log_file)
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    return logger


def write_json_file(target, output_dir):
    with open(output_dir, 'w') as f:
        json.dump(target, f)


def chord_map_function():
    chord_maps = {}
    with open('data/chord_note_map.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            key, value = line.split('-')
            chord_maps[key] = value.replace('\n', '')
    return chord_maps

def convert_json_chord(json_lead_sheet, chord_map):
    for measure in json_lead_sheet['measures']:
        for chord in measure:
            notes = ','.join(chord['chord'])
            if notes in chord_map:
                parts = chord_map[notes].split(';')
                chord['chord'] = [int(x) for x in parts[0].split(',')]
                if len(parts) > 1:
                    chord['scale'] = parts[1]
    return json_lead_sheet


def convert_note_series(note, chord_map):
    if type(note) == Harmony:
        chord_str = ','.join([str(x) for x in note.chord])
        if chord_str in chord_map:
            parts = chord_map[chord_str].split(';')
            note.chord = [int(x) for x in parts[0].split(',')]
            if len(parts) > 1:
                note.chord_scale = parts[1]
        return note
    else:
        chord_str = ','.join([str(x) for x in note['chord']])
        if chord_str in chord_map:
            parts = chord_map[chord_str].split(';')
            note['chord'] = [int(x) for x in parts[0].split(',')]
            if len(parts) > 1:
                note['scale'] = parts[1]
        return note


def convert_instrument_name(target_instrument, instrument_list):
    if len(instrument_list) == 1:
        instrument_suffix = 'Solo'
    else:
        instrument_shortcut = []
        if 'Piano' in instrument_list:
            instrument_shortcut.append('Pf')
        if 'Bass' in instrument_list:
            instrument_shortcut.append('Bs')
        if 'Drums' in instrument_list or 'Percussion' in instrument_list:
            instrument_shortcut.append('Ds')
        if 'Guitar' in instrument_list:
            instrument_shortcut.append('Gt')
        instrument_shortcut = sorted(instrument_shortcut)
        instrument_suffix = ','.join(instrument_shortcut)
    return target_instrument + '_' + instrument_suffix

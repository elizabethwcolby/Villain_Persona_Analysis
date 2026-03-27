"""
File: parser.py
Author: Elizabeth Colby
Description: Parses through and cleans the data files
"""
import re
import csv

class VillainDialogueParser:

    def __init__(self, villain_mappings, stopwords: str=None):
        self.villain_mappings = villain_mappings
        self.stopwords = self._load_stopwords(stopwords)
        self.villain_patterns = self._build_patterns()

    def _load_stopwords(self, stopwords):
        with open('stopwords.txt', 'r') as f:
            return set(word.strip().lower() for word in f if word.strip())



    def _build_patterns(self):
        patterns = {}
        for used_name, name_variations in self.villain_mappings.items():
            name_options = '|'.join(re.escape(name) for name in name_variations)

            pattern = rf'^\s*({name_options})(\s*\([^)]*\))?\s*:?\s*$'
            patterns[used_name] = re.compile(pattern, re.IGNORECASE | re.MULTILINE)

        return patterns

    def extract_dialogue(self, script_text: str, script_name: str = ""):
        results = []
        lines = script_text.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i]

            matched = False
            for used_name, pattern in self.villain_patterns.items():
                match = pattern.match(line)

                if match:
                    block = self._collect_block(lines, i)

                    if block['dialogue'].strip():
                        block['villain'] = used_name
                        block['movie'] = script_name
                        block['line_number'] = i + 1
                        results.append(block)

                    i += block['lines_consumed']
                    matched = True
                    break

            if not matched:
                i += 1

        return results


    def _collect_block(self, lines, start_idx):
        dialogue_lines = []
        direction_lines = []
        current_idx = start_idx + 1

        char_line = lines[start_idx].strip()
        if '(' in char_line and ')' in char_line:
            pass

        while current_idx < len(lines):
            line = lines[current_idx]

            if self._is_new_character(line):
                break

            if self._is_scene_heading(line):
                break

            if line.strip().startswith('(') and line.strip().endswith(')'):
                direction_lines.append(line.strip())

            elif '(' in line.strip() and ')' in line.strip() and not line.strip().startswith('('):
                dialogue_lines.append(line.strip())

            elif line.strip() and not self._is_transition(line):
                if self._is_production_note(line.strip()):
                    current_idx += 1
                    continue

                dialogue_lines.append(line.strip())
            elif not line.strip() and dialogue_lines:
                if current_idx + 1 < len(lines):
                    next_line = lines[current_idx+1].strip()
                    if not next_line or self._is_scene_heading(lines[current_idx+1]):
                        break
            current_idx += 1

        return {'dialogue' : ' '.join(dialogue_lines),
                'direction' : ' '.join(direction_lines),
                'lines_consumed' : current_idx - start_idx}

    def _is_new_character(self, line):
        """ If a new character speaks, the text block won't be added to the villain's text block"""
        stripped = line.strip()
        if not stripped:
            return False

        without_parens = re.sub(r'\([^)]*\)', '', stripped)
        without_colon = without_parens.rstrip(':').strip()

        if without_colon and without_colon.isupper() and len(without_colon) < 50:
            words = without_colon.lower().split()

            if any(word in self.stopwords for word in words):
                return False
            return True
        return False

    def _is_scene_heading(self, line):
        stripped = line.strip()
        return (stripped.startswith(('INT.', 'EXT.', 'INT/', 'EXT/')) or
                (stripped and stripped[0].isdigit() and ('INT.' in stripped or 'EXT.' in stripped)))

    def _is_transition(self, line):
        stripped = line.strip().upper()
        transitions = ['CUT TO:', 'FADE IN:', 'FADE OUT:', 'DISSOLVE TO:', 'JUMP CUT:', 'SMASH CUT:', 'MATCH CUT:']
        return any(stripped.endswith(trans) for trans in transitions)

    def _is_production_note(self, line):
        line_lower = line.lower()
        production_markers = [
            'rev.', 'revision', 'draft',
            'continued', "cont'd", 'contd',
            '(more)', '(cont\'d)',
            'prod #', 'production'
        ]

        if re.search(r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}', line):
            return True

        if re.match(r'^\d+\.\s*$', line):
            return True

        return any(marker in line_lower for marker in production_markers)


    def get_dialogue_stats(self, dialogues):
        stats = {}

        for dialogue in dialogues:
            villain = dialogue['villain']
            if villain not in stats:
                stats[villain] = {'total_lines' : 0,
                                  'total_words' : 0,
                                  'avg_words_per_line' : 0}
            stats[villain]['total_lines'] += 1
            word_count = len(dialogue['dialogue'].split())
            stats[villain]['total_words'] += word_count

        # find averages
        for villain in stats:
            if stats[villain]['total_lines'] > 0:
                stats[villain]['avg_words_per_line'] = (stats[villain]['total_words'] / stats[villain]['total_lines'])

        return stats

VILLAIN_CONFIG = {'Patrick Bateman' : ['BATEMAN', 'PATRICK BATEMAN', 'MCCLANE'],
                  'Thanos' : ['THANOS'],
                  'Hans Gruber' : ['HANS', 'HANS GRUBER', 'GRUBER'],
                  'Darth Vader' : ['VADER', 'DARTH VADER'],
                  'Joker' : ['JOKER', 'ARTHUR FLECK', 'ARTHUR', 'FLECK'],
                  'Scar' : ['SCAR'],
                  'Norman Bates' : ['NORMAN', 'BATES', 'NORMAN BATES'],
                  'Jack Torrance' : ['JACK', 'JACK TORRANCE'],
                  'Hannibal Lecter' : ['LECTER', 'HANNIBAL LECTER', 'HANNIBAL', 'DR. LECTER', 'DR LECTER'],
                  'Delbert Grady' : ['GRADY', 'DELBERT GRADY']}

SCRIPT_FILES = {
    'American Psycho': 'scripts/American_Psycho_Script.txt',
    'Avengers: Endgame': 'scripts/Avengers_Endgame_Script.txt',
    'Die Hard': 'scripts/Die_Hard_Script.txt',
    'The Empire Strikes Back': 'scripts/Empire_Strikes_Back_Script.txt',
    'Joker': 'scripts/Joker_Script.txt',
    'The Lion King': 'scripts/Lion_King_Script.txt',
    'Psycho': 'scripts/Psycho_Script.txt',
    'The Silence of the Lambs': 'scripts/Silence_of_the_Lambs_Script.txt',
    'The Shining': 'scripts/The_Shining_Script.txt'
}

def process_scripts(script_files, villain_config, stopwords):
    parser = VillainDialogueParser(villain_config, stopwords)
    all_dialogue = []

    for script_name, file_path in script_files.items():
        print(f"Collecting from {script_name}...")
        with open(file_path, 'r') as f:
            script_text = f.read()

        dialogue = parser.extract_dialogue(script_text, script_name)
        all_dialogue.extend(dialogue)

        print(f"Extracted {len(dialogue)} dialogue blocks")

    return all_dialogue

def save_as_csv(dialogues, output: str='villain_dialogues.csv'):
    with open(output, 'w', newline='') as f:
        fieldnames = ['villain', 'movie', 'line_number', 'dialogue', 'direction', 'word_count']
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        for d in dialogues:
            writer.writerow({'villain' : d['villain'],
                             'movie' : d['movie'],
                             'line_number' : d['line_number'],
                             'dialogue' : d['dialogue'],
                             'direction' : d.get('direction'),
                             'word_count' : len(d['dialogue'].split())
            })

    print(f"Saved {len(dialogues)} dialogue blocks to {output}")


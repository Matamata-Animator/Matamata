from typing import Iterator, List, Dict, Any, Iterable
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import ToneAnalyzerV3
from ibm_watson.tone_analyzer_v3 import ToneInput

tone_analyzer: ToneAnalyzerV3


class TonedSentence:
    tone: str
    text: str

    def __init__(self, tone: str, text: str):
        self.tone = tone
        self.text = text


def init(api_url: str, api_key: str) -> None:
    global tone_analyzer
    authenticator = IAMAuthenticator(api_key)
    tone_analyzer = ToneAnalyzerV3(
        version='2017-09-21',
        authenticator=authenticator
    )
    tone_analyzer.set_service_url(api_url)


def save_emotions(script_file: str, new_file: str) -> None:
    with open(script_file, 'r') as script, open(new_file, 'w+') as new_script:
        emotion_sentences = gen_emotions(script.read())
        for sentence in emotion_sentences:
            new_script.write(f'[{sentence.tone}] {sentence.text} ')


def gen_emotions(script: str) -> List[TonedSentence]:
    final_result = []
    for batch in gen_batches(script):
        result = tone_analyzer.tone(ToneInput(''.join(batch)), sentences=True).get_result()
        for sentence in result['sentences_tone']:
            final_result.append(process_ibm_sentence(sentence))
    return final_result


def gen_batches(script: str, batch_size: int = 100) -> Iterator[List[str]]:
    last_index = 0
    current_batch = []
    for i in range(len(script)):
        if script[i] in ['.', '?', '!']:
            current_batch.append(script[last_index:i+1])
            last_index = i+1
            if len(current_batch) == batch_size:
                yield current_batch
                current_batch = []
    yield current_batch


def process_ibm_sentence(sentence_info) -> TonedSentence:
    tones = sentence_info['tones']
    text = sentence_info['text']

    if not tones:
        return TonedSentence('Default', text)

    best_tone = max(tones, key=lambda t: t['score'])
    return TonedSentence(best_tone['tone_name'], text)

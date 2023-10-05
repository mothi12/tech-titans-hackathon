def extract_aws_speaker_partition_trasnscripts(data, asText=False):
    # Extract speaker segments and transcript items
    speaker_segments = data['results']['speaker_labels']['segments']
    transcript_items = data['results']['items']

    speaker_transcripts = []
    if asText:
        speaker_transcripts = ""

    for segment in speaker_segments:
        speaker_label = segment['speaker_label']
        start_time = float(segment['start_time'])
        end_time = float(segment['end_time'])

        transcript = ""
        for item in transcript_items:
            if 'start_time' in item:
                item_start_time = float(item['start_time'])
                item_end_time = float(item['end_time'])
                if item_start_time >= start_time and item_end_time <= end_time:
                    if item['type'] == 'pronunciation':
                        transcript += item['alternatives'][0]['content'] + " "

        if asText:
            speaker_transcripts += "{speaker_label}: {transcript} \n".format(speaker_label=speaker_label,
                                                                             transcript=transcript)
        else:
            speaker_transcripts.append({speaker_label: transcript})
        print(f"{speaker_label}: {transcript}")
    return speaker_transcripts

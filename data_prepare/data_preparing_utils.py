import os
import json
import random


def merge_answer_span_family(data_dir, save_dir, target_datatype):
    print(os.listdir(data_dir))
    target_data_filenames = [f for f in os.listdir(data_dir) if 'TL' in f and
                             any(datatype in f for datatype in target_datatype)]

    domain = 'admin'
    merged_data = {
        'version': 'merged_data_' + domain + '_answer_span_family',
        'data': []
    }
    for target_filename in target_data_filenames:
        with open(os.path.join(data_dir, target_filename)) as j:
            target_data = json.load(j)

        merged_data['data'] += target_data['data']

    merged_data_filename = merged_data['version'] + '.json'

    print('saving {} ... '.format(merged_data_filename), end='')
    with open(os.path.join(save_dir, merged_data_filename), 'w') as j:
        json.dump(merged_data, j, indent='\t', ensure_ascii=False)
    print('Done!!')


def shuffle_multi_choice_option(data_dir, save_dir):
    phase = ['TL', 'VL']
    data_filenames = [f for f in os.listdir(data_dir) if f.endswith('.json') and 'multiple_choice' in f
                      and 'shuffled' not in f]
    data_filenames = [f for f in data_filenames if any(p in f for p in phase)]
    for data_filename in data_filenames:
        with open(os.path.join(data_dir, data_filename)) as j:
            data = json.load(j)

        for entry in data['data']:
            for paragraph in entry['paragraphs']:
                for qa in paragraph['qas']:
                    options = qa['answers']['options']
                    random.shuffle(options)

        shuffled_data_filename = 'shuffled_' + data_filename
        print('saving {} ... '.format(shuffled_data_filename), end='')
        with open(os.path.join(save_dir, shuffled_data_filename), 'w') as j:
            json.dump(data, j, indent='\t', ensure_ascii=False)
        print('Done!!')


def show_data_info(data_dir, target_file_list):
    def _show_each_data_info(target_file_path):
        with open(target_file_path) as json_file:
            target_data = json.load(json_file)

        data_type = target_data['data'][0]['paragraphs'][0]['qas'][0]['qa_type']
        dataset_info_format = {
            'total_samples': 0,
            'context_num': 0,
            'avg_context_length': 0,
            'avg_question_length': 0
        }
        if data_type == 5:
            dataset_info_format['Yes_samples'] = 0
            dataset_info_format['No_samples'] = 0
        elif data_type == 6:
            dataset_info_format['answer_1_samples'] = 0
            dataset_info_format['answer_2_samples'] = 0
            dataset_info_format['answer_3_samples'] = 0
            dataset_info_format['answer_4_samples'] = 0
        else:
            dataset_info_format['avg_answer_length'] = 0
            dataset_info_format['positive_samples'] = 0
            dataset_info_format['negative_samples'] = 0

        for entry in target_data['data']:
            for paragraph in entry['paragraphs']:
                dataset_info_format['context_num'] += 1
                dataset_info_format['avg_context_length'] += len(paragraph['context'])
                for qa in paragraph['qas']:
                    dataset_info_format['total_samples'] += 1
                    dataset_info_format['avg_question_length'] += len(qa['question'])
                    if qa['qa_type'] == 5:
                        yesno_key = qa['answers']['text'] + '_samples'
                        try:
                            dataset_info_format[yesno_key] += 1
                        except KeyError:
                            pass
                    elif qa['qa_type'] == 6:
                        answer_text = qa['answers']['text']
                        answer_option = str(qa['answers']['options'].index(answer_text) + 1)
                        option_key = 'answer_' + answer_option + '_samples'
                        dataset_info_format[option_key] += 1
                    else:
                        try:
                            if not qa['is_impossible']:
                                dataset_info_format['positive_samples'] += 1
                                dataset_info_format['avg_answer_length'] += len(qa['answers']['text'])
                            else:
                                dataset_info_format['negative_samples'] += 1
                        except KeyError:
                            dataset_info_format['positive_samples'] += 1
                            dataset_info_format['avg_answer_length'] += len(qa['answers']['text'])

        dataset_info_format['avg_context_length'] = dataset_info_format['avg_context_length'] / dataset_info_format[
            'context_num']
        dataset_info_format['avg_question_length'] = dataset_info_format['avg_question_length'] / dataset_info_format[
            'total_samples']
        if 'avg_answer_length' in dataset_info_format.keys():
            try:
                dataset_info_format['avg_answer_length'] = \
                    dataset_info_format['avg_answer_length'] / dataset_info_format['positive_samples']
            except ZeroDivisionError:
                dataset_info_format['avg_answer_length'] = 0

        print(target_file_path.split('/')[-1])
        for k, v in dataset_info_format.items():
            if 'length' not in k:
                print('\t# of {}: {}'.format(k, v))
        print('\taverage context length: {}'.format(dataset_info_format['avg_context_length']))
        print('\taverage question length: {}'.format(dataset_info_format['avg_question_length']))
        try:
            print('\taverage answer length: {}'.format(dataset_info_format['avg_answer_length']))
        except KeyError:
            pass

    for dk, dv in target_file_list.items():
        print('\n', '=' * 15, dk, '=' * 15)
        tmp_paths = [data_dir + '/' + filename for filename in dv if len(filename) > 0]
        for tmp_path in tmp_paths:
            _show_each_data_info(tmp_path)
            print('-' * 60)



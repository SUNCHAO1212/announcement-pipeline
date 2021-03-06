import re


def title2label(title):
    """ TODO 完善精细分类体系，包含+不包含 """
    labels = {} 
    # classes = {
    #    "增持":{
    #         "计划":"",
    #         "进展":"",
    #         "结果":"",
    #    },
    #    "减持":{
    #         "计划":"",
    #         "进展":"",
    #         "结果":"",
    #    },
    # }
    classes = {
        "减持": {
            "计划": "",
        },
        "增持": {
            "计划": "",
        },
        "股权": {
            "质押": "",
        }
    }
    classes_list = list(classes.keys())
    for pattern_str in classes_list :			#尝试匹配level1分类，即["增持","减持"]
        pattern = re.compile(pattern_str)
        if pattern.search(title) :
            labels['level1'] = pattern_str
            sub_classes_list = list(classes[pattern_str].keys())
            for sub_pattern_str in sub_classes_list :	#尝试匹配level2分类
                sub_pattern = re.compile(sub_pattern_str)
                if sub_pattern.search(title) :
                    labels['level2'] = sub_pattern_str
 
    if 'level1' not in labels:
        labels['level1'] = '其他'
        labels['level2'] = '其他'
    if 'level2' not in labels:
        labels['level2'] = '其他'

    # return labels
    if labels['level1'] == '其他' or labels['level2'] == '其他':
        event_type = '其他'
    else:
        event_type = '股东' + labels['level1'] + labels['level2'] + '事件'
    return event_type




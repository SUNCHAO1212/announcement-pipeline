import re


def title2label(title):

    labels = {} 
    # classes = {
    #    r"增持":{
    #         r"计划":"",
    #         r"进展":"",
    #         r"结果":"",
    #    },
    #    r"减持":{
    #         r"计划":"",
    #         r"进展":"",
    #         r"结果":"",
    #    },
    # }
    classes = {
        "减持": {
            "计划": "",
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
 
    if not 'level1' in labels :
        labels['level1'] = '其他'
        labels['level2'] = '其他'
    if not 'level2' in labels :
        labels['level2'] = '其他'
    return labels




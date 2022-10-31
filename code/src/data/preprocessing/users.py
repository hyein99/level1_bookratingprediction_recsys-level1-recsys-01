import pandas as pd
from . import get_apply_map_series

def age_map(x: int) -> int:

    x = int(x)
    if x < 10:
        return 1
    elif x >= 10 and x < 20:
        return 2
    elif x >= 20 and x < 30:
        return 3
    elif x >= 30 and x < 40:
        return 4
    elif x >= 40 and x < 50:
        return 5
    elif x >= 50 and x < 60:
        return 6
    else:
        return 7

def country_map(x):

    if x in ['','na']:
        return 'usa'
    elif x in ['unitedstatesofamerica','losestadosunidosdenorteamerica','us','unitedstate','unitedstaes','unitedstatesofamerica','unitedsates','unitedstates']:
        return 'usa'
    elif x in ['england','uk','unitedkingdom','unitedkindgonm']:
        return 'unitedkingdom'
    elif x in ['deutschland']:
        return 'germany'
    elif x in ['catalunya','espaa']:
        return 'spain'
    else :
        return x

def remove_outlier_by_age( target_data : pd.DataFrame, target_age:int)->pd.DataFrame:
    
    if 'age' not in target_data.columns:
        raise Exception( '[delete_outlier_of_age] age column not in target_data')
    
    tmp_idx = target_data[target_data['age'] > target_age].index
    
    return target_data.drop(tmp_idx)

def process_location( target_data : pd.DataFrame, process_level:int )->pd.DataFrame:
    
    if 'location' not in target_data.columns:
        raise Exception( '[preprocess_location] location column not in target_data')

    level_map = { 1 : 'country' , 2 : 'city', 3:'state'}
    # location 특수 문자 제거
    target_data['location'].str.replace(r'[^0-9a-zA-Z:,]+', '',regex = True )
    basic_str = 'location_'
    
    if process_level >= 1 : 
        cur_str = basic_str + level_map[1]
        target_data[cur_str] = target_data['location'].apply(lambda x: x.split(',')[2])
        target_data[cur_str] = target_data[cur_str].apply(country_map)

    if process_level >= 2 :
        cur_str = basic_str + level_map[2]
        target_data[cur_str] = target_data['location'].apply(lambda x: x.split(',')[1])
    
    if process_level >= 3 :
        cur_str = basic_str + level_map[3]
        target_data[cur_str] = target_data['location'].apply(lambda x: x.split(',')[0])
    
    target_data = target_data.drop(['location'], axis=1)
    return target_data


def process_age( target_data : pd.DataFrame,  how : object = 'mean') -> pd.DataFrame:
    """
    target dataframe 에 age column 이 있을 경우, 
    column 의 결측치를  'how' parameter 에 전달된 값으로 채운다.
    - 현재는 'mean'만 적용 
    """

    if 'age' not in target_data.columns:
        print( '[process_age] age column not in target_data')
        return None
    
    if  'mean' == how :
        target_data['age'] = target_data['age'].fillna(int(target_data['age'].mean()))

    target_data['age'] = get_apply_map_series(target_data,'age', age_map)

    return target_data

# gu 작가별 단골 추가
def add_regular_custom_by_author( target_data:pd.DataFrame)->pd.DataFrame:  

    common = target_data.groupby(['book_author', 'user_id'])[['rating']].count()
    author_common = common[common['rating']>2].groupby('book_author').count().sort_values('rating', ascending=False).rename(columns={'rating': 'author_common_cnt'}).reset_index()
    target_data = target_data.merge(author_common, on='book_author', how='left')
    target_data['author_common_cnt'].fillna(0, inplace=True)

    return target_data
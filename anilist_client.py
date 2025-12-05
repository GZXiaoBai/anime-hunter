import requests
import streamlit as st

# 使用 st.cache_data 缓存 API 请求，避免重复调用 Anilist 导致变慢或超限
@st.cache_data(ttl=3600)
def get_anime_info(anilist_id):
    """
    根据 Anilist ID 获取动漫元数据（标题、封面）
    """
    if not anilist_id:
        return None

    url = 'https://graphql.anilist.co'
    query = '''
    query ($id: Int) {
      Media (id: $id, type: ANIME) {
        title {
          romaji
          english
          native
        }
        coverImage {
          large
          medium
        }
        format
        episodes
        isAdult
      }
    }
    '''
    
    variables = {'id': anilist_id}

    try:
        response = requests.post(url, json={'query': query, 'variables': variables}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', {}).get('Media')
        else:
            print(f"Anilist API Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Anilist Request Failed: {e}")
        return None

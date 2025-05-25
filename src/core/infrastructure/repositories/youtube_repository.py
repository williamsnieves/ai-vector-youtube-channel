from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Optional
from datetime import datetime
from ...domain.interfaces import YouTubeRepository
from ...domain.entities import Channel, Video
from config.settings import get_settings

class YouTubeRepositoryImpl(YouTubeRepository):
    def __init__(self):
        settings = get_settings()
        self.youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)

    async def get_channel_info(self, channel_id: str) -> Channel:
        try:
            # Get channel details
            channel_response = self.youtube.channels().list(
                part='snippet,statistics',
                id=channel_id
            ).execute()

            channel_data = channel_response['items'][0]
            snippet = channel_data['snippet']
            statistics = channel_data['statistics']

            # Get channel videos
            videos = await self.get_channel_videos(channel_id)

            return Channel(
                channel_id=channel_id,
                title=snippet['title'],
                description=snippet['description'],
                subscriber_count=int(statistics['subscriberCount']),
                video_count=int(statistics['videoCount']),
                videos=videos
            )
        except HttpError as e:
            raise Exception(f"Error fetching channel info: {str(e)}")

    async def get_channel_videos(self, channel_id: str, max_results: int = 50) -> List[Video]:
        try:
            # First, get the uploads playlist ID
            channel_response = self.youtube.channels().list(
                part='contentDetails',
                id=channel_id
            ).execute()
            
            uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

            # Get videos from the uploads playlist
            videos = []
            next_page_token = None

            while len(videos) < max_results:
                playlist_response = self.youtube.playlistItems().list(
                    part='snippet',
                    playlistId=uploads_playlist_id,
                    maxResults=min(50, max_results - len(videos)),
                    pageToken=next_page_token
                ).execute()

                for item in playlist_response['items']:
                    video_id = item['snippet']['resourceId']['videoId']
                    video_details = self.youtube.videos().list(
                        part='snippet,statistics',
                        id=video_id
                    ).execute()

                    video_data = video_details['items'][0]
                    snippet = video_data['snippet']
                    statistics = video_data['statistics']

                    video = Video(
                        video_id=video_id,
                        title=snippet['title'],
                        description=snippet['description'],
                        published_at=datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00')),
                        view_count=int(statistics.get('viewCount', 0)),
                        like_count=int(statistics.get('likeCount', 0)),
                        comment_count=int(statistics.get('commentCount', 0)),
                        tags=snippet.get('tags', [])
                    )
                    videos.append(video)

                next_page_token = playlist_response.get('nextPageToken')
                if not next_page_token:
                    break

            return videos
        except HttpError as e:
            raise Exception(f"Error fetching channel videos: {str(e)}")

    async def get_video_transcript(self, video_id: str) -> Optional[str]:
        try:
            # Note: Getting transcripts requires additional setup with youtube_transcript_api
            # This is a placeholder for the actual implementation
            return None
        except Exception as e:
            raise Exception(f"Error fetching video transcript: {str(e)}") 
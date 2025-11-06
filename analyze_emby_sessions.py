#!/usr/bin/env python3
"""
Detailed Emby Session Analysis
Analyzes all active sessions to understand session types and states
"""
import sys
import os
import json
import requests
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Add the plexpy directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plexpy'))

from env_config import get_emby_config


def analyze_emby_sessions():
    """Analyze all Emby sessions in detail"""
    print("="*80)
    print("DETAILED EMBY SESSION ANALYSIS")
    print("="*80)
    
    # Load configuration
    config = get_emby_config()
    
    # Disable SSL warnings if SSL verification is disabled
    if not config['ssl_verify']:
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    
    try:
        headers = {'X-Emby-Token': config['api_key']}
        
        response = requests.get(
            f"{config['url']}/Sessions",
            headers=headers,
            timeout=config['timeout'],
            verify=config['ssl_verify']
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get sessions: {response.status_code}")
            return
        
        sessions = response.json()
        print(f"Total sessions found: {len(sessions)}")
        print("="*80)
        
        # Group sessions by type
        active_playback = []
        inactive_sessions = []
        api_sessions = []
        
        for i, session in enumerate(sessions):
            print(f"\n--- SESSION {i+1} ---")
            
            # Basic session info
            user_name = session.get('UserName', 'Unknown')
            user_id = session.get('UserId', 'N/A')
            client = session.get('Client', 'Unknown')
            device_name = session.get('DeviceName', 'Unknown')
            device_id = session.get('DeviceId', 'N/A')
            app_version = session.get('ApplicationVersion', 'N/A')
            
            print(f"User: {user_name} (ID: {user_id})")
            print(f"Client: {client}")
            print(f"Device: {device_name}")
            print(f"Device ID: {device_id}")
            print(f"App Version: {app_version}")
            
            # Session activity info
            last_activity = session.get('LastActivityDate', 'N/A')
            last_playback = session.get('LastPlaybackCheckIn', 'N/A')
            is_active = session.get('IsActive', False)
            supports_remote_control = session.get('SupportsRemoteControl', False)
            
            print(f"Last Activity: {last_activity}")
            print(f"Last Playback: {last_playback}")
            print(f"Is Active: {is_active}")
            print(f"Remote Control: {supports_remote_control}")
            
            # Now playing info
            now_playing = session.get('NowPlayingItem')
            if now_playing:
                media_type = now_playing.get('Type', 'Unknown')
                name = now_playing.get('Name', 'Unknown')
                series_name = now_playing.get('SeriesName', '')
                season = now_playing.get('ParentIndexNumber', '')
                episode = now_playing.get('IndexNumber', '')
                
                print(f"🎬 NOW PLAYING:")
                print(f"   Type: {media_type}")
                print(f"   Title: {name}")
                if series_name:
                    print(f"   Series: {series_name}")
                if season and episode:
                    print(f"   S{season:02d}E{episode:02d}")
                
                # Play state
                play_state = session.get('PlayState', {})
                if play_state:
                    position_ticks = play_state.get('PositionTicks', 0)
                    is_paused = play_state.get('IsPaused', False)
                    is_muted = play_state.get('IsMuted', False)
                    volume_level = play_state.get('VolumeLevel', 0)
                    
                    position_ms = position_ticks // 10000  # Convert ticks to milliseconds
                    position_seconds = position_ms // 1000
                    hours = position_seconds // 3600
                    minutes = (position_seconds % 3600) // 60
                    seconds = position_seconds % 60
                    
                    print(f"   Position: {hours:02d}:{minutes:02d}:{seconds:02d}")
                    print(f"   Paused: {is_paused}")
                    print(f"   Volume: {volume_level}% {'(Muted)' if is_muted else ''}")
                
                active_playback.append(session)
            else:
                print("📱 No active playback")
                if 'API' in client or client == 'API Development':
                    api_sessions.append(session)
                else:
                    inactive_sessions.append(session)
            
            # Transcoding info
            transcode_info = session.get('TranscodingInfo')
            if transcode_info:
                print(f"🔄 TRANSCODING:")
                print(f"   Audio Codec: {transcode_info.get('AudioCodec', 'N/A')}")
                print(f"   Video Codec: {transcode_info.get('VideoCodec', 'N/A')}")
                print(f"   Container: {transcode_info.get('Container', 'N/A')}")
                print(f"   Is Video Direct: {transcode_info.get('IsVideoDirect', 'N/A')}")
                print(f"   Is Audio Direct: {transcode_info.get('IsAudioDirect', 'N/A')}")
        
        # Summary
        print("\n" + "="*80)
        print("SESSION SUMMARY")
        print("="*80)
        print(f"Total Sessions: {len(sessions)}")
        print(f"Active Playback Sessions: {len(active_playback)}")
        print(f"Inactive Client Sessions: {len(inactive_sessions)}")
        print(f"API/Development Sessions: {len(api_sessions)}")
        
        if active_playback:
            print(f"\n🎬 ACTIVE PLAYBACK SESSIONS ({len(active_playback)}):")
            for session in active_playback:
                user = session.get('UserName', 'Unknown')
                client = session.get('Client', 'Unknown')
                device = session.get('DeviceName', 'Unknown')
                now_playing = session.get('NowPlayingItem', {})
                title = now_playing.get('Name', 'Unknown')
                play_state = session.get('PlayState', {})
                is_paused = play_state.get('IsPaused', False)
                state = "⏸️  Paused" if is_paused else "▶️  Playing"
                
                print(f"   • {user} on {client} ({device}) - {title} [{state}]")
        
        print("\n" + "="*80)
        return sessions
        
    except Exception as e:
        print(f"❌ Error analyzing sessions: {e}")
        return None


if __name__ == "__main__":
    analyze_emby_sessions()
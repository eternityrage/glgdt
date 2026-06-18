import os
import json
import glob
import random
import requests
import shutil
import sys
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

try:
    from upload.upload_instagram import upload_to_instagram
    from upload.upload_threads import upload_to_threads
    from upload.upload_facebook import upload_to_facebook, upload_to_facebook_story
    from upload.upload_to_youtube import upload_to_youtube
except ImportError as e:
    print(f"Error importing upload modules: {e}")
    pass

PROCESSED_DIR = "Processed_Videos"
PUBLISHED_LOG = "published_videos.json"

def get_already_published():
    if os.path.exists(PUBLISHED_LOG):
        with open(PUBLISHED_LOG, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def get_repost_counts():
    published = get_already_published()
    counts = {}
    for entry in published:
        vname = entry.get("video_name", "")
        counts[vname] = counts.get(vname, 0) + 1
    return counts

def mark_as_published(video_name, metadata):
    published = get_already_published()
    published.append({
        "video_name": video_name,
        "metadata": metadata
    })
    with open(PUBLISHED_LOG, 'w', encoding='utf-8') as f:
        json.dump(published, f, indent=4)

def select_video(specific_video=None):
    published = [item["video_name"] for item in get_already_published()]
    all_videos = sorted(glob.glob(os.path.join(PROCESSED_DIR, "*.mp4")))

    if specific_video:
        if os.path.exists(specific_video):
            vid_path = specific_video
            name = os.path.basename(specific_video)
        else:
            vid_path = os.path.join(PROCESSED_DIR, specific_video)
            name = specific_video

        if os.path.exists(vid_path):
            if name in published:
                post_count = sum(1 for p in published if p == name)
                print(f"Video {name} was already published ({post_count}x) - Re-publishing (recycling)")
            return vid_path, name
        else:
            print(f"Error: Specific video {name} not found")
            return None, None

    unpublished = [(vid, os.path.basename(vid)) for vid in all_videos if os.path.basename(vid) not in published]

    if unpublished:
        vid, name = unpublished[0]
        return vid, name

    if all_videos:
        repost_counts = get_repost_counts()
        weights = []
        for vid in all_videos:
            name = os.path.basename(vid)
            count = repost_counts.get(name, 0)
            weight = max(1, 1000 // (3 ** min(count, 6)))
            weights.append(weight)

        selected_vid = random.choices(all_videos, weights=weights, k=1)[0]
        name = os.path.basename(selected_vid)
        post_count = repost_counts.get(name, 0)
        print(f"All videos published. Weighted random reuse (posted {post_count}x): {name}")
        return selected_vid, name

    return None, None

def generate_caption():
    import random
    import time

    api_key = os.getenv("POLLINATIONS_API_KEY")
    model = os.getenv("AI_MODEL", "openai")

    fallback_titles = [
        "Gal Gadot's Most Iconic Red Carpet Looks of All Time",
        "Gal Gadot Singing 'Imagine' — Pure Magic",
        "Gal Gadot's Best Wonder Woman Moments That Broke the Internet",
        "Gal Gadot as Wonder Woman — The Performance That Defined a Generation",
        "Gal Gadot Interview Moments That Proved She's a Star",
        "Gal Gadot on the Red Carpet — Hollywood Queen Strikes Again",
        "Gal Gadot's Funniest Talk Show Moments Compilation",
        "Gal Gadot Talks Wonder Woman 3 — What We Know",
        "The Rise of Gal Gadot — From Miss Israel to Hollywood Superstar",
        "Gal Gadot as Diana Prince — Every Iconic Scene",
        "Gal Gadot and Dwayne Johnson — Cutest Moments Ever",
        "Gal Gadot's Best Fashion Moments You Need to See",
        "Gal Gadot Behind the Scenes — She's So Real",
        "Gal Gadot at the Oscars — History in the Making",
        "Gal Gadot's Action Scenes That Left Us Speechless",
    ]

    fallback_descriptions = [
        "Gal Gadot doesn't just walk red carpets — she owns them. From her stunning Tom Ford gown at the Wonder Woman premiere to that breathtaking Givenchy at the Oscars, every look is a moment. She works with her stylist to create fashion history every single time. The way she carries herself, the confidence, the elegance — it's unmatched. Drop a fire emoji if you think Gal Gadot is the most elegant celebrity of our generation! #galgadot #galgadotstyle #redcarpet #fashionicon #wonderwoman #celebrityfashion #hollywoodstyle #galgadotfan #oscars #dceu #justiceleague #fashiongoals #icon",
        "When Gal Gadot sings 'Imagine' with other celebrities, the world stops. Her voice, her presence, that incredible message of hope — it was pure magic. The video became an instant global sensation and showed the world that Gal Gadot is not just an actress, she's a force for good. Like if you still get chills watching this! #galgadot #imagine #galgadotsinging #hollywood #celebrity #viral #galgadotfan #hope #music",
        "Gal Gadot's portrayal of Diana Prince in Wonder Woman is one of the greatest superhero performances in cinema history. The strength, the compassion, the power — she brought something real to every single scene. From the No Man's Land scene to the final battle with Ares, she left us speechless. Share this if you think Gal Gadot is the BEST Wonder Woman! #galgadot #wonderwoman #dianaprice #dcuniverse #warnerbros #superhero #galgadotfan #action #empowerment",
        "When Gal Gadot was cast as Wonder Woman, she made history. But when the movie released, she cemented her legacy. Her performance is heartfelt, powerful, and inspiring. She reminded us that there's beauty in strength. Gal Gadot is proof that hard work, talent, and staying true to yourself pays off. Comment below with your favorite Gal Gadot movie! #galgadot #wonderwoman #historymaker #hollywood #actress #dceu #superhero #galgadotfan #action",
        "Gal Gadot on the interview circuit is an absolute joy to watch. Whether she's sharing stories about her daughters or giving profound answers about representation in Hollywood, she lights up every room. Her chemistry with interviewers is unmatched — she's funny, sharp, thoughtful, and down-to-earth. Like if you could watch Gal Gadot interviews all day! #galgadot #interviews #talkshow #hollywood #celebrity #galgadotfan #funny",
        "Before she was Wonder Woman, Gal Gadot was a beauty queen! At 18, she won Miss Israel and went on to compete in Miss Universe. But that was just the beginning. From modeling to Fast & Furious to becoming one of the highest-paid actresses in the world, she's proven that hard work and determination pay off. Follow for more Gal Gadot content! #galgadot #missisrael #beautyqueen #model #fastandfurious #hollywood #galgadotfan",
        "Fashion has never seen a powerhouse quite like Gal Gadot. Each red carpet appearance is a masterclass in style — from Old Hollywood elegance at the Oscars to modern chic at premieres. The way she carries herself with grace and confidence makes every look iconic. Comment which Gal Gadot look is your favorite! #galgadot #fashionicon #style #redcarpet #galgadotfan #elegance",
        "Gal Gadot's talk show appearances are pure gold! From teaching Jimmy Fallon Hebrew to playing games with James Corden, she always brings the energy. Her stories are captivating and she never takes herself too seriously. She's the celebrity everyone wants to interview because you never know what she'll do next. Like if Gal Gadot's laugh is your favorite sound! #galgadot #funnymoments #fallon #corden #talkshow #comedy #hollywood",
        "From her breakthrough role in Fast & Furious to her iconic performance as Wonder Woman, Gal Gadot has become one of the most versatile actors of her generation. She doesn't just play characters — she becomes them. Whether it's the fierce Gisele, the heroic Diana Prince, or the cunning characters in her thrillers, she disappears into every role. Follow for daily Gal Gadot content! #galgadot #wonderwoman #fastandfurious #hollywood #actress #movies #galgadotfan",
        "Gal Gadot's journey from Miss Israel to Hollywood superstar is nothing short of inspirational. She started as a model, served in the Israeli military, and proved everyone wrong with every step. She's used her platform to speak up about important causes and inspire women around the world. She's not just a star — she's a role model for an entire generation. Share this if Gal Gadot inspires you! #galgadot #inspiration #hollywood #successstory #rolemodel #galgadotfan",
        "Gal Gadot's Wonder Woman in the DCEU is absolutely iconic. From the explosive entrance in Batman v Superman to the emotional journey in Wonder Woman 1984, she brought depth and humanity to the role. The chemistry between Gal Gadot and Chris Pine made their relationship one of the most beloved in superhero cinema. Like if you love Gal Gadot as Wonder Woman! #galgadot #wonderwoman #dceu #dc #warnerbros #chrisspine #superhero #galgadotfan",
        "Gal Gadot is one of the most elegant and talented actresses in Hollywood. From her action-packed roles to her dramatic performances, she continues to captivate audiences worldwide. Her dedication to her craft, her philanthropic work, and her positive energy make her a true star. Drop a heart if you agree! #galgadot #hollywood #actress #elegance #talent #galgadotfan",
        "Gal Gadot's style evolution is one for the history books. From her early modeling days to becoming a full-blown fashion icon working with the biggest designers in the world. She's not afraid to take risks and makes every look look effortless. Every single look tells a story. Follow for style inspiration from the queen herself! #galgadot #fashion #styleevolution #icon #celebrityfashion #redcarpet #galgadotfan",
        "There's something about Gal Gadot behind the scenes that makes her even more lovable. The way she hypes up her co-stars, the genuine friendships she's built on set, the silly moments between takes, the kindness she shows to crew members — she's the real deal. Everyone who works with her says she's one of the most professional, humble, and talented people they've ever met. Hollywood needs more stars like Gal Gadot. Like if you agree! #galgadot #bts #behindthescenes #real #authentic #hollywood #kindness #galgadotfan",
        "Gal Gadot at award shows is appointment viewing. Year after year, she delivers some of the most talked-about moments in Hollywood history. Her grace, her elegance, her incredible speeches — she doesn't just attend award shows, she lights them up. Her commitment to her craft and her ability to inspire is unmatched. Comment your favorite Gal Gadot movie moment! #galgadot #oscars #awards #hollywood #actress #galgadotfan",
    ]

    if not api_key:
        chosen_title = random.choice(fallback_titles)
        chosen_desc = random.choice(fallback_descriptions)
        print("Warning: POLLINATIONS_API_KEY not found. Using fallback captions.")
        return chosen_title, chosen_desc

    vibes = [
        "exciting and celebratory — hype up Gal Gadot's talent, style, and iconic moments",
        "fun and engaging — make it feel like you're talking about your favorite celebrity with a friend",
        "inspiring and uplifting — highlight how Gal Gadot's journey motivates her fans",
        "glamorous and stylish — focus on her incredible fashion and red carpet looks",
        "emotional and heartfelt — showcase her powerful acting and the moments that move us",
        "funny and lighthearted — capture her amazing personality and hilarious interview moments",
        "nostalgic and throwback — celebrate her journey from Miss Israel to Hollywood superstardom",
    ]
    chosen_vibe = random.choice(vibes)

    prompt = (
        f"Write a completely unique, long, and captivating title and description for a short video "
        f"about Gal Gadot for the Facebook page 'Gal Gadot Daily'. "
        f"The page posts the best Gal Gadot moments — red carpet looks, interviews, acting scenes, "
        f"fashion, behind-the-scenes, and everything that makes Gal Gadot a Hollywood icon. "
        f"Speak as a passionate Gal Gadot fan who loves celebrating her talent and style. "
        f"Make the vibe {chosen_vibe}. "
        f"The description should be LONG (4-6 sentences minimum), deeply engaging, and fun. "
        f"Include engagement calls-to-action such as: "
        f"- Like if you love Gal Gadot! "
        f"- Comment your favorite Gal Gadot movie or role! "
        f"- Share this with another Gal Gadot fan! "
        f"- Follow Gal Gadot Daily for the best Gal Gadot content! "
        f"Include relevant hashtags in ALL LOWERCASE such as #galgadot #hollywood #wonderwoman #diana #fastandfurious #galgadotstyle #fashion #celebrity #redcarpet #galgadotfan #actress #superhero #movies #justiceleague. "
        f"Return ONLY a valid JSON object in this format: {{\"title\": \"<title>\", \"description\": \"<description>\"}} "
        f"Do not include any other text or markdown block backticks."
    )

    url = "https://gen.pollinations.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.9,
        "seed": random.randint(1, 999999)
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        content = data.get('choices', [{}])[0].get('message', {}).get('content', '')

        content = content.replace("```json", "").replace("```", "").strip()
        result = json.loads(content)

        chosen_title = random.choice(fallback_titles)
        chosen_desc = random.choice(fallback_descriptions)
        return result.get("title", chosen_title), result.get("description", chosen_desc)
    except Exception as e:
        print(f"Error generating caption: {e}")
        return random.choice(fallback_titles), random.choice(fallback_descriptions)

def main():
    print("=" * 60)
    print("DAILY AUTOMATION STARTING")
    print("=" * 60)
    
    specific_video = sys.argv[1] if len(sys.argv) > 1 else None
    video_path, video_name = select_video(specific_video)
    if not video_path:
        print("No new videos found to publish. Exiting.")
        return
        
    print(f"Selected Video: {video_name}")
    print("Generating caption via Pollination AI...")
    title, description = generate_caption()
    
    print(f"Title: {title}")
    print(f"Description:\n{description}")
    
    combined_caption = f"{title}\n\n{description}"
    
    success_flags = {
        "instagram_reel": False,
        "instagram_story": False,
        "facebook_reel": False,
        "facebook_story": False,
        "threads": False,
        "youtube": False
    }
    
    try:
        result = upload_to_instagram(video_path, combined_caption, is_story=False)
        if result and result.get('status') == 'skipped':
            print(f"Instagram Reel: Skipped ({result.get('reason', 'No credentials')})")
        else:
            success_flags["instagram_reel"] = True
    except Exception as e:
        print(f"Instagram Reel upload failed: {e}")
        
    try:
        result = upload_to_instagram(video_path, combined_caption, is_story=True)
        if result and result.get('status') == 'skipped':
            print(f"Instagram Story: Skipped ({result.get('reason', 'No credentials')})")
        else:
            success_flags["instagram_story"] = True
    except Exception as e:
        print(f"Instagram Story upload failed: {e}")
        
    try:
        result = upload_to_facebook(video_path, description, title=title)
        if result and result.get('status') == 'skipped':
            print(f"Facebook Reel: Skipped ({result.get('reason', 'No credentials')})")
        else:
            success_flags["facebook_reel"] = True
    except Exception as e:
        print(f"Facebook Reel upload failed: {e}")
        
    try:
        result = upload_to_facebook_story(video_path)
        if result and result.get('status') == 'skipped':
            print(f"Facebook Story: Skipped ({result.get('reason', 'No credentials')})")
        else:
            success_flags["facebook_story"] = True
    except Exception as e:
        print(f"Facebook Story upload failed: {e}")
        
    try:
        result = upload_to_threads(video_path, combined_caption)
        if result and result.get('status') == 'skipped':
            print(f"Threads: Skipped ({result.get('reason', 'No credentials')})")
        else:
            success_flags["threads"] = True
    except Exception as e:
        print(f"Threads upload failed: {e}")
        
    try:
        upload_to_youtube(video_path, title, description, tags=["galgadot", "hollywood", "wonderwoman", "diana", "fastandfurious", "galgadotstyle", "fashion", "celebrity", "red carpet", "galgadot fan", "actress", "superhero", "movies", "justice league", "galgadot daily"])
        success_flags["youtube"] = True
    except Exception as e:
        print(f"YouTube upload failed: {e}")
        
    print("\nMarking video as published.")
    
    published_list = get_already_published()
    is_recycled = any(item["video_name"] == video_name for item in published_list)
    
    if is_recycled:
        print(f"   This is a recycled video (re-publishing)")
    
    mark_as_published(video_name, {
        "title": title,
        "description": description,
        "success_flags": success_flags,
        "recycled": is_recycled
    })
    
    published_dir = "Published_Videos"
    if not os.path.exists(published_dir):
        os.makedirs(published_dir)
        
    try:
        dest_path = os.path.join(published_dir, video_name)
        shutil.move(video_path, dest_path)
        print(f"Moved published video to {dest_path}")
    except Exception as e:
        print(f"Failed to move published video: {e}")
    
    print("DAILY AUTOMATION COMPLETE")

if __name__ == "__main__":
    main()

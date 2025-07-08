import requests
import time
import random
from typing import List, Dict, Optional
from app.domain.interfaces.services import IPokeAPIService
from app.domain.entities.post import Post
from app.domain.entities.comment import Comment
from app.infrastructure.external.circuit_breaker import CircuitBreaker

class PokeAPIService(IPokeAPIService):
    BASE_URL = "https://pokeapi.co/api/v2/berry"
    
    def __init__(self, circuit_breaker: CircuitBreaker = None):
        self.circuit_breaker = circuit_breaker or CircuitBreaker(
            failure_threshold=5,
            reset_timeout=60
        )

    def get_all_posts(self) -> List[Dict]:
        if self.circuit_breaker.is_open():
            raise Exception("Circuit breaker is open - PokeAPI is unavailable")

        try:
            response = requests.get(f"{self.BASE_URL}/")
            response.raise_for_status()
            return response.json()['results']
        except requests.exceptions.RequestException as e:
            self.circuit_breaker.record_failure()
            raise Exception(f"Failed to fetch posts from PokeAPI: {e}")

    def get_post_details(self, post_id: int) -> Optional[Dict]:
        if self.circuit_breaker.is_open():
            raise Exception("Circuit breaker is open - PokeAPI is unavailable")

        try:
            response = requests.get(f"{self.BASE_URL}/{post_id}/")
            response.raise_for_status()
            self.circuit_breaker.record_success()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.circuit_breaker.record_failure()
            raise Exception(f"Failed to fetch post details from PokeAPI: {e}")

    def fetch_and_transform_posts(self) -> List[Post]:
        posts_data = self._retry(self.get_all_posts)
        posts = []
        
        for post_data in posts_data:
            post_id = int(post_data['url'].split('/')[-2])
            try:
                details = self._retry(lambda: self.get_post_details(post_id))
                if details:
                    post = Post(
                        id=post_id,
                        name=details['name'],
                        growth_time=details['growth_time'],
                        max_harvest=details['max_harvest'],
                        natural_gift_power=details['natural_gift_power'],
                        size=details['size'],
                        smoothness=details['smoothness'],
                        soil_dryness=details['soil_dryness'],
                        raw_data=details
                    )
                    posts.append(post)
            except Exception as e:
                print(f"Error processing post {post_id}: {e}")
                continue
                
        return posts

    def fetch_comments_for_post(self, post: Post) -> List[Comment]:
        try:
            details = self._retry(lambda: self.get_post_details(post.id))
            if not details or 'flavors' not in details:
                return []
                
            return [Comment.create(post.id, flavor) for flavor in details['flavors']]
        except Exception as e:
            print(f"Error fetching comments for post {post.id}: {e}")
            return []

    def _retry(self, func, max_retries=3, initial_delay=1, max_delay=10):
        retries = 0
        delay = initial_delay
        
        while retries < max_retries:
            try:
                return func()
            except Exception as e:
                retries += 1
                if retries == max_retries:
                    raise
                    
                # Add jitter to avoid thundering herd problem
                sleep_time = min(delay * (2 ** retries) + random.uniform(0, 1), max_delay)
                time.sleep(sleep_time)
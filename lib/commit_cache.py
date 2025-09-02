import os
import json
import hashlib
import subprocess
from datetime import datetime
from pathlib import Path


class CommitCache:
    def __init__(self, cache_dir=".cache/git"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_repo_hash(self, repo_path):
        """Generate a hash for the repo path to use as cache key"""
        return hashlib.md5(repo_path.encode()).hexdigest()[:12]
    
    def _get_cache_file(self, repo_path, cache_type):
        """Get cache file path for a repository"""
        repo_hash = self._get_repo_hash(repo_path)
        return self.cache_dir / f"{repo_hash}_{cache_type}.json"
    
    def _get_repo_head_hash(self, repo_path):
        """Get the current HEAD hash to detect changes"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"], 
                cwd=repo_path, 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except:
            return None
    
    def get_cached_commits(self, repo_path, since_date):
        """Get cached commits for a repo, or None if cache is invalid"""
        cache_file = self._get_cache_file(repo_path, "commits")
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache is still valid
            current_head = self._get_repo_head_hash(repo_path)
            if current_head != cache_data.get('head_hash'):
                return None
            
            # Check if cached since_date is older or equal to requested
            cached_since = datetime.fromisoformat(cache_data.get('since_date', ''))
            # Make timezone-aware comparison
            if since_date.tzinfo is None:
                since_date = since_date.replace(tzinfo=cached_since.tzinfo)
            elif cached_since.tzinfo is None:
                cached_since = cached_since.replace(tzinfo=since_date.tzinfo)
            if cached_since > since_date:
                return None
            
            # Filter commits to requested date range
            filtered_commits = []
            for commit in cache_data.get('commits', []):
                commit_date = datetime.fromisoformat(commit['timestamp'])
                # Handle timezone comparison
                if since_date.tzinfo is None:
                    since_date_cmp = since_date.replace(tzinfo=commit_date.tzinfo)
                elif commit_date.tzinfo is None:
                    since_date_cmp = since_date
                    commit_date = commit_date.replace(tzinfo=since_date.tzinfo)
                else:
                    since_date_cmp = since_date
                    
                if commit_date >= since_date_cmp:
                    filtered_commits.append(commit)
            
            return filtered_commits
            
        except Exception as e:
            print(f"Error reading cache for {repo_path}: {e}")
            return None
    
    def cache_commits(self, repo_path, commits, since_date):
        """Cache commits for a repository"""
        cache_file = self._get_cache_file(repo_path, "commits")
        
        try:
            current_head = self._get_repo_head_hash(repo_path)
            
            cache_data = {
                'head_hash': current_head,
                'since_date': since_date.isoformat(),
                'cached_at': datetime.now().isoformat(),
                'commits': []
            }
            
            # Convert commits to serializable format
            for commit in commits:
                cache_data['commits'].append({
                    'timestamp': commit['timestamp'].isoformat(),
                    'hash': commit['hash'],
                    'message': commit['message'],
                    'repo': commit['repo'],
                    'module': commit['module'],
                    'type': commit['type'],
                    'branch_type': commit['branch_type'],
                    'intention': commit['intention'],
                    'risk': commit['risk']
                })
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
        except Exception as e:
            print(f"Error caching commits for {repo_path}: {e}")
    
    def get_cached_master_main_hashes(self, repo_path):
        """Get cached master/main branch hashes"""
        cache_file = self._get_cache_file(repo_path, "branches")
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache is still valid
            current_head = self._get_repo_head_hash(repo_path)
            if current_head != cache_data.get('head_hash'):
                return None
            
            return set(cache_data.get('master_main_hashes', []))
            
        except Exception as e:
            print(f"Error reading branch cache for {repo_path}: {e}")
            return None
    
    def cache_master_main_hashes(self, repo_path, hashes):
        """Cache master/main branch hashes"""
        cache_file = self._get_cache_file(repo_path, "branches")
        
        try:
            current_head = self._get_repo_head_hash(repo_path)
            
            cache_data = {
                'head_hash': current_head,
                'cached_at': datetime.now().isoformat(),
                'master_main_hashes': list(hashes)
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
        except Exception as e:
            print(f"Error caching branches for {repo_path}: {e}")
    
    def clear_cache(self):
        """Clear all cache files"""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
        print(f"Cleared cache directory: {self.cache_dir}")
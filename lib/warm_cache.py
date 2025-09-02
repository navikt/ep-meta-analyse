#!/usr/bin/env python3
"""
Cache warming script for commit data.
Populates the git cache with commit data going back to 2022-01-01.
"""
import time
from datetime import datetime
from .commit_data_cached import gather_changes_from_subprojects_cached

def warm_cache():
    """Warm the cache with full commit history"""
    root_dir = "../"
    startdate = datetime(2022, 1, 1)  # Full history from 2022
    duration = datetime.now() - startdate
    
    print("Warming cache with commit data from 2022-01-01...")
    print(f"Duration: {duration.days} days")
    
    start_time = time.time()
    
    changes = gather_changes_from_subprojects_cached(root_dir, duration, verbose=True)
    
    end_time = time.time()
    
    print(f"Cache warming completed in {end_time - start_time:.2f} seconds")
    print(f"Total commits cached: {len(changes)}")
    
    # Show breakdown by repository
    repos = {}
    for change in changes:
        repo = change['repo']
        if repo not in repos:
            repos[repo] = 0
        repos[repo] += 1
    
    print(f"\nBreakdown by repository:")
    for repo, count in sorted(repos.items(), key=lambda x: x[1], reverse=True):
        print(f"  {repo}: {count} commits")

if __name__ == "__main__":
    warm_cache()
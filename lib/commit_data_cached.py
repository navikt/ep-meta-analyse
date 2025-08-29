import subprocess
from datetime import datetime
from .repos import projects_info
from .commit_cache import CommitCache
from .commit_data import (
    intention_from_message, 
    risk_from_message, 
    text_intention, 
    text_risk,
    risks,
    intentions
)



def gather_changes_from_subprojects_cached(root_dir, duration, verbose=False):
    """Cached version of gather_changes_from_subprojects"""
    since_date = datetime.now() - duration
    cache = CommitCache()
    
    changes = []
    for project_info in projects_info(root_dir):
        project_path = root_dir + '/' + project_info["path"]
        if verbose:
            print(f"Processing {project_info['path']}...")
        
        # Try to get cached commits
        cached_commits = cache.get_cached_commits(project_path, since_date)
        
        if cached_commits is not None:
            if verbose:
                print(f"  Using cached data: {len(cached_commits)} commits")
            # Convert cached commits back to proper datetime objects
            for commit in cached_commits:
                commit['timestamp'] = datetime.fromisoformat(commit['timestamp'])
            changes.extend(cached_commits)
        else:
            if verbose:
                print(f"  Cache miss - fetching fresh data...")
            # Fetch fresh data
            project_commits_data = get_project_commits_with_branches(root_dir, project_info, duration, verbose)
            
            # Process commits
            repo_changes = []
            for commit_data in project_commits_data:
                timestamp, hash, subject, branch_type = commit_data
                
                commit_info = {
                    "repo": project_info["path"],
                    "timestamp": datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S %z"),
                    "module": project_info["module"],
                    "type": project_info["type"],
                    "hash": hash,
                    "message": subject,
                    "branch_type": branch_type,
                    "intention": intention_from_message(subject),
                    "risk": risk_from_message(subject)
                }
                repo_changes.append(commit_info)
            
            if verbose:
                print(f"  Fetched {len(repo_changes)} commits - caching...")
            
            # Cache the results
            cache.cache_commits(project_path, repo_changes, since_date)
            changes.extend(repo_changes)
    
    return changes


def get_project_commits_with_branches(root_dir, project_info, duration, verbose=False):
    """Get commits with branch information efficiently"""
    hours, remainder = divmod(duration.total_seconds(), 3600)
    report_period = "%d hours" % (hours + (1 if remainder > 0 else 0))
    
    path = root_dir + '/' + project_info["path"]
    cache = CommitCache()
    
    # Try to get cached master/main hashes
    master_main_hashes = cache.get_cached_master_main_hashes(path)
    
    if master_main_hashes is None:
        if verbose:
            print(f"    Fetching master/main branches...")
        # Get commits on master/main branches
        master_main_cmd = subprocess.run(
            ["sh", "-c", 
             f"git fetch --all >/dev/null && "
             f"(git log master --format='%h' --since='{report_period}' 2>/dev/null || true; "
             f"git log main --format='%h' --since='{report_period}' 2>/dev/null || true) | sort -u"],
            cwd=path, stdout=subprocess.PIPE, text=True)
        
        master_main_hashes = set(master_main_cmd.stdout.strip().split('\n')) if master_main_cmd.stdout.strip() else set()
        
        # Cache the master/main hashes
        cache.cache_master_main_hashes(path, master_main_hashes)
        if verbose:
            print(f"    Cached {len(master_main_hashes)} master/main hashes")
    else:
        if verbose:
            print(f"    Using cached master/main branches: {len(master_main_hashes)} hashes")
    
    # Get all commits for the period
    commit_format_string = f"%ci€%h€%s"
    project_changes_cmd = subprocess.run(
        ["sh", "-c",
         f"git fetch --all >/dev/null && git log --all --format='{commit_format_string}' --since='{report_period}'"],
        cwd=path, stdout=subprocess.PIPE, text=True)
    
    commit_lines = project_changes_cmd.stdout.split('\n')
    commits_with_branches = []
    
    for line in commit_lines:
        if line:
            parts = line.split("€")
            if len(parts) >= 3:
                timestamp, hash, subject = parts[0], parts[1], "€".join(parts[2:])
                branch_type = 'M' if hash in master_main_hashes else 'B'
                commits_with_branches.append((timestamp, hash, subject, branch_type))
    
    return commits_with_branches
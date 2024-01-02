import requests
import json
import concurrent.futures

def get_user_numbers_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            user_numbers = [line.strip().split('/')[-1] for line in file.readlines()]
        return user_numbers
    except Exception as e:
        print(f"Error reading user numbers from file: {e}")
        return []

def log_http_response(user_number, group_occurrences):
    try:
        # Construct the URL based on the user input
        url_to_log = f"https://groups.roblox.com/v1/users/{user_number}/groups/roles?includeLocked=true"

        # Make an HTTP GET request to the constructed URL
        response = requests.get(url_to_log)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()

            # Extract and log relevant information for each group
            output_file_path = "output_log.txt"
            with open(output_file_path, 'a', encoding='utf-8') as file:
                file.write('\n\n')  # Add two new lines
                file.write(f"Output for user number {user_number}:\n\n")

                for group_data in data.get("data", []):
                    group_info = group_data.get("group", {})
                    role_info = group_data.get("role", {})
                    group_id = group_info.get("id")
                    group_name = group_info.get("name")
                    member_count = group_info.get("memberCount")

                    file.write(f"Group ID: {group_id}, Group Name: {group_name}, Member Count: {member_count}\n")

                    # Update group occurrences
                    group_occurrences[group_id] = group_occurrences.get(group_id, 0) + 1

            print(f"Successfully logged the output for user number {user_number}")
        else:
            print(f"Error: Unable to fetch data from {url_to_log}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def process_user_numbers(user_numbers, group_occurrences):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Process each user number with multi-threading
        futures = [executor.submit(log_http_response, user_number, group_occurrences) for user_number in user_numbers]
        concurrent.futures.wait(futures)

# Read user numbers from input.txt file
user_numbers = get_user_numbers_from_file("input.txt")

# Process each user number with multi-threading
group_occurrences = {}
process_user_numbers(user_numbers, group_occurrences)

# Log duplicate group occurrences to duplicate_stats.txt
duplicate_stats_file_path = "duplicate_stats.txt"
with open(duplicate_stats_file_path, 'w', encoding='utf-8') as duplicate_stats_file:
    duplicate_stats_file.write("Duplicate Group Statistics:\n\n")
    for group_id, occurrences in group_occurrences.items():
        if occurrences > 1:
            duplicate_stats_file.write(f"Group ID: {group_id}, Occurrences: {occurrences}\n")

print(f"Duplicate statistics logged to {duplicate_stats_file_path}")

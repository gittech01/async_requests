import asyncio
import aiohttp

# GitHub GraphQL API endpoint
url = 'https://api.github.com/graphql'

# Personal access token
access_token = 'YOUR_ACCESS_TOKEN'

# Define the GraphQL query
query = '''
query ($owner: String!, $name: String!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    collaborators(first: 100, after: $cursor) {
      pageInfo {
        endCursor
        hasNextPage
      }
      edges {
        node {
          login
          createdAt
        }
      }
    }
  }
}
'''

# Define the start and end dates of the desired interval
start_date = '2023-01-01T00:00:00Z'
end_date = '2023-06-30T23:59:59Z'

# Define the list of repositories
repositories = [
    {'owner': 'owner1', 'name': 'repo1'},
    {'owner': 'owner2', 'name': 'repo2'},
    # Add more repositories as needed
]

# Define headers with access token
headers = {'Authorization': f'Bearer {access_token}'}


async def fetch_members(session, repository):
    members = []
    cursor = None
    has_next_page = True

    while has_next_page:
        variables = {'owner': repository['owner'], 'name': repository['name'], 'cursor': cursor}

        # Make the GraphQL request for a single page of results
        async with session.post(url, headers=headers, json={'query': query, 'variables': variables}) as response:
            data = await response.json()

        collaborators = data['data']['repository']['collaborators']
        edges = collaborators['edges']
        for edge in edges:
            member = edge['node']
            if start_date <= member['createdAt'] <= end_date:
                members.append(member['login'])

        has_next_page = collaborators['pageInfo']['hasNextPage']
        if has_next_page:
            cursor = collaborators['pageInfo']['endCursor']

    return members


async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for repository in repositories:
            task = asyncio.create_task(fetch_members(session, repository))
            tasks.append(task)

        # Gather all the tasks and wait for them to complete
        results = await asyncio.gather(*tasks)

        # Print the filtered member usernames for each repository
        for repository, result in zip(repositories, results):
            owner = repository['owner']
            name = repository['name']
            print(f"Members of repository {owner}/{name} within the date interval:")
            for member in result:
                print(member)
            print()


# Run the main async function
asyncio.run(main())
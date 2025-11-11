
# Create a new branch

## Overview
Given a description for a task, create a new branch

## Steps
1. **Ingest the message put in and clean up the message**
   - You must take in the message and clean it to be succinct and clear. 

2. **Summarize the message into a branch**
   - The branch should be relatively short, less than 63 characters
   - if i provide a ticket number number like "ENT-1234" in the beginning, reference that at the beginning of the new summarize message. (ex: ENT-1234-my-branch)
   - each word should be followed by - until the last word
   - Validate that the branch name doesn't already exist
   - Validate that the ticket number format is valid (e.g., numeric)
   - Handle cases where the message is too long after summarization by truncating appropriately

3. **Create the branch**
   - using the message in step 2, create the branch
   - If branch creation fails (e.g., branch already exists), inform the user and do not proceed

## RULES YOU MUST FOLLOW
   - never do this if there is no message given by the user
   - never do this if the user does not provide a ticket number
   - Validate all inputs before attempting branch creation
   - Handle errors gracefully and provide clear feedback to the user

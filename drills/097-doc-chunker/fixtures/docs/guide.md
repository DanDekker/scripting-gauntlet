# Setup

Install the tool with pip.   
Then run guide --help.

This paragraph is repeated
across two documents.

## Usage

Run the command with a path.

The command walks every markdown file under the given directory, splits it into
sections at level-one headings, and then splits each section into paragraphs so
that the indexer can embed the pieces one at a time without blowing the model's
context window on a single giant document that would otherwise be truncated.

# Troubleshooting

If it fails, read the log. 

import logging
import gitlab
import hashlib
from src.config.settings import supersettings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s', handlers=[logging.StreamHandler()])

class GitlabService:
    def __init__(self, project_id, merge_request_id):
        self.project_id = project_id
        self.merge_request_id = merge_request_id
        gitlab_url = supersettings.GITLAB_URL
        gitlab_token = supersettings.GITLAB_TOKEN
        self.gl = gitlab.Gitlab(gitlab_url, private_token=gitlab_token)

    async def get_diffs(self):
        try:
            logging.info(f"Fetching diffs for project {self.project_id} and merge request {self.merge_request_id}")
            project = self.gl.projects.get(self.project_id)
            merge_request = project.mergerequests.get(self.merge_request_id)
            all_diffs = merge_request.changes()
            return all_diffs
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return None

    async def post_comment(self, body):
        try:
            project = self.gl.projects.get(self.project_id)
            merge_request = project.mergerequests.get(self.merge_request_id)
            merge_request.notes.create({'body': body})
            logger.debug(f"Comment posted to merge request {self.merge_request_id}")
        except Exception as e:
            logger.error(f"An error occurred: {e}")

    async def edit_comment(self, comment_id, body):
        try:
            project = self.gl.projects.get(self.project_id)
            merge_request = project.mergerequests.get(self.merge_request_id)
            note = merge_request.notes.get(comment_id)
            note.body = body
            note.save()
            logger.debug(f"Comment {comment_id} edited in merge request {self.merge_request_id}")
        except Exception as e:
            logger.error(f"An error occurred: {e}")

    async def post_comment_on_diff(self, diff_id, body, position):
        try:
            project = self.gl.projects.get(self.project_id)
            merge_request = project.mergerequests.get(self.merge_request_id)

            # Ensure position contains all required fields
            required_fields = ['position_type', 'new_line', 'old_path', 'new_path', 'base_sha', 'start_sha', 'head_sha']
            missing_fields = [field for field in required_fields if field not in position]
            if missing_fields:
                logger.error(f"Missing required fields in position: {missing_fields}")
                return {"error": f"Missing required fields in position: {missing_fields}"}

            # Check if the file exists
            old_path = position['old_path']
            new_path = position['new_path']
            base_sha = position['base_sha']
            head_sha = position['head_sha']

            try:
                project.files.get(file_path=old_path, ref=base_sha)
            except gitlab.exceptions.GitlabGetError:
                logger.warning(f"File {old_path} does not exist in the base branch. Checking new path.")

            try:
                project.files.get(file_path=new_path, ref=head_sha)
            except gitlab.exceptions.GitlabGetError:
                return {"error": f"File {new_path} does not exist in the head branch."}

            # Generate line_code
            line_code = hashlib.sha1(f"{new_path}_{position['new_line']}".encode()).hexdigest()

            discussion = {
                'body': body,
                'position': {
                    'base_sha': base_sha,
                    'start_sha': position['start_sha'],
                    'head_sha': head_sha,
                    'position_type': position['position_type'],
                    'new_path': new_path,
                    'old_path': old_path,
                    'old_line': position.get('old_line', None),
                    'new_line': position['new_line'],
                    'line_code': line_code,
                }
            }
            logging.debug(f"Discussion: {discussion}")
            merge_request.discussions.create(discussion)
            logger.debug(f"Comment posted to diff {diff_id} in merge request {self.merge_request_id}")
            return {"message": "Comment posted successfully"}
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return {"error": str(e)}
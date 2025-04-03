import logging
import gitlab
import hashlib
from src.config.settings import supersettings

logger = logging.getLogger(__name__)

class GitlabService:
    def __init__(self, project_id: int, merge_request_id: int):
        """
        Initialize the GitlabService with project and merge request IDs.

        Args:
            project_id (int): The ID of the GitLab project.
            merge_request_id (int): The ID of the merge request.
        """
        self.project_id = project_id
        self.merge_request_id = merge_request_id
        gitlab_url = supersettings.GITLAB_URL
        gitlab_token = supersettings.GITLAB_TOKEN
        self.gl = gitlab.Gitlab(gitlab_url, private_token=gitlab_token)

    async def get_diffs(self) -> dict:
        """
        Fetch the diffs for the specified merge request.

        Returns:
            dict: The diffs of the merge request.

        Raises:
            Exception: If an error occurs while fetching the diffs.
        """
        try:
            logger.info(f"Fetching diffs for project {self.project_id} and merge request {self.merge_request_id}")
            project = self.gl.projects.get(self.project_id)
            merge_request = project.mergerequests.get(self.merge_request_id)
            all_diffs = merge_request.changes()
            return all_diffs
        except Exception as e:
            logger.error(f"An error occurred while fetching diffs: {e}")
            return {}

    async def post_comment(self, body: str) -> None:
        """
        Post a comment to the specified merge request.

        Args:
            body (str): The body of the comment.

        Raises:
            Exception: If an error occurs while posting the comment.
        """
        try:
            project = self.gl.projects.get(self.project_id)
            merge_request = project.mergerequests.get(self.merge_request_id)
            merge_request.notes.create({'body': body})
            logger.debug(f"Comment posted to merge request {self.merge_request_id}")
        except Exception as e:
            logger.error(f"An error occurred while posting a comment: {e}")

    async def edit_comment(self, comment_id: int, body: str) -> None:
        """
        Edit an existing comment in the specified merge request.

        Args:
            comment_id (int): The ID of the comment to edit.
            body (str): The new body of the comment.

        Raises:
            Exception: If an error occurs while editing the comment.
        """
        try:
            project = self.gl.projects.get(self.project_id)
            merge_request = project.mergerequests.get(self.merge_request_id)
            note = merge_request.notes.get(comment_id)
            note.body = body
            note.save()
            logger.debug(f"Comment {comment_id} edited in merge request {self.merge_request_id}")
        except Exception as e:
            logger.error(f"An error occurred while editing a comment: {e}")

    async def update_description(self, body: str) -> None:
        """
        Update the description of the specified merge request.

        Args:
            body (str): The new description of the merge request.

        Raises:
            Exception: If an error occurs while updating the description.
        """
        try:
            project = self.gl.projects.get(self.project_id)
            merge_request = project.mergerequests.get(self.merge_request_id)
            merge_request.description = body
            merge_request.save()
            logger.debug(f"Description updated for merge request {self.merge_request_id}")
        except Exception as e:
            logger.error(f"An error occurred while updating the description: {e}")

    async def post_comment_on_diff(self, diff_id: int, body: str, position: dict) -> dict:
        """
        Post a comment on a specific diff in the merge request.

        Args:
            diff_id (int): The ID of the diff.
            body (str): The body of the comment.
            position (dict): The position details for the comment.

        Returns:
            dict: A message indicating the result of the operation.

        Raises:
            Exception: If an error occurs while posting the comment.
        """
        try:
            project = self.gl.projects.get(self.project_id)
            merge_request = project.mergerequests.get(self.merge_request_id)

            required_fields = ['position_type', 'new_line', 'old_path', 'new_path', 'base_sha', 'start_sha', 'head_sha']
            missing_fields = [field for field in required_fields if field not in position]
            if missing_fields:
                logger.error(f"Missing required fields in position: {missing_fields}")
                return {"error": f"Missing required fields in position: {missing_fields}"}

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
            logger.debug(f"Discussion: {discussion}")
            merge_request.discussions.create(discussion)
            logger.debug(f"Comment posted to diff {diff_id} in merge request {self.merge_request_id}")
            return {"message": "Comment posted successfully"}
        except Exception as e:
            logger.error(f"An error occurred while posting a comment on diff: {e}")
            return {"error": str(e)}
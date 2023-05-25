from rest_framework.exceptions import APIException

from rest_framework import status


class NonexistentProjectException(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, project: str):
        super().__init__(f"Project {project} does not exist")


class NonexistentVersionException(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, project: str, version: str):
        super().__init__(f"Version '{version}' for project '{project}' does not exist")


class NonexistentCategoryException(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, project: str, version: str, category: str):
        super().__init__(
            f"Category '{category}' does not exist for project '{project}', version '{version}'"
        )


class EmptyCategoryException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, project: str, version: str, category: str):
        super().__init__(
            f"No data exists for project '{project}', version '{version}', and category '{category}'"
        )


class MissingAPIKeyException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "No API key provided"


class InvalidAPIKeyException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Incorrect API key provided"


class InvalidDataException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST


# Maybe?
class AlreadyExistsException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

class CustomException(Exception):
    def __init__(self, detail: str, **kwargs):
        self.detail = detail.format(**kwargs)
        super().__init__(self.detail)


class ErrorStartingApp(CustomException):
    def __init__(self, e, **kwargs):
        super().__init__(detail=f"Error starting app: {e}", **kwargs)


class ErrorPostgresSQL(CustomException):
    def __init__(self, e, **kwargs):
        super().__init__(detail=f"Error checking PostgresSQL connection: {e}", **kwargs)


class ErrorRedis(CustomException):
    def __init__(self, e, **kwargs):
        super().__init__(detail=f"Error checking Redis connection: {e}", **kwargs)


class ObjectNotFound(CustomException):
    def __init__(self, **kwargs):
        super().__init__(detail="{object_type} with ID {object_id} not found.", **kwargs)


class UserNotFound(ObjectNotFound):
    def __init__(self, user_id: str):
        super().__init__(object_type="User", object_id=user_id)


class CompanyNotFound(ObjectNotFound):
    def __init__(self, company_id: str):
        super().__init__(object_type="Company", object_id=company_id)


class InvitationNotFound(ObjectNotFound):
    def __init__(self, invitation_id: str):
        super().__init__(object_type="Invitation", object_id=invitation_id)


class QuizNotFound(ObjectNotFound):
    def __init__(self, quiz_id: str):
        super().__init__(object_type="Quiz", object_id=quiz_id)


class QuestionNotFound(ObjectNotFound):
    def __init__(self, quiz_id: str):
        super().__init__(object_type="Question", object_id=quiz_id)


class ErrorRetrieving(CustomException):
    def __init__(self, **kwargs):
        super().__init__(detail="Error retrieving {object_type}: {e}", **kwargs)


class ErrorRetrievingList(ErrorRetrieving):
    def __init__(self, e):
        super().__init__(object_type="list", e=e)


class ErrorRetrievingUser(ErrorRetrieving):
    def __init__(self, e):
        super().__init__(object_type="User", e=e)


class ErrorRetrievingCompany(ErrorRetrieving):
    def __init__(self, e):
        super().__init__(object_type="Company", e=e)


class ErrorRetrievingMember(ErrorRetrieving):
    def __init__(self, e):
        super().__init__(object_type="Member", e=e)


class ErrorRetrievingToken(ErrorRetrieving):
    def __init__(self, e):
        super().__init__(object_type="Token", e=e)


class ErrorRetrievingCurrentUser(ErrorRetrieving):
    def __init__(self, e):
        super().__init__(object_type="Current User", e=e)


class ErrorRetrievingInvited(ErrorRetrieving):
    def __init__(self, e):
        super().__init__(object_type="invited users for Company", e=e)


class ErrorRetrievingMembershipUser(ErrorRetrieving):
    def __init__(self, e):
        super().__init__(object_type="membership requests for User", e=e)


class ErrorRetrievingMembershipCompany(ErrorRetrieving):
    def __init__(self, e):
        super().__init__(object_type="membership requests for Company", e=e)


class ErrorRetrievingInvitation(ErrorRetrieving):
    def __init__(self, e):
        super().__init__(object_type="invitations for User", e=e)


class ErrorRetrievingAdmin(ErrorRetrieving):
    def __init__(self, e):
        super().__init__(object_type="admins for company", e=e)


class ErrorRetrievingQuiz(ErrorRetrieving):
    def __init__(self, e):
        super().__init__(object_type="Quiz", e=e)


class ErrorRetrievingQuestion(ErrorRetrieving):
    def __init__(self, e):
        super().__init__(object_type="Question", e=e)


class AlreadyExists(CustomException):
    def __init__(self, **kwargs):
        super().__init__(detail="{object_type} already exists.", **kwargs)


class AlreadyExistsUser(AlreadyExists):
    def __init__(self):
        super().__init__(object_type="User")


class AlreadyExistsCompany(AlreadyExists):
    def __init__(self):
        super().__init__(object_type="Company")


class AlreadyExistsInvitation(AlreadyExists):
    def __init__(self):
        super().__init__(object_type="Invitation")


class AlreadyExistsMember(AlreadyExists):
    def __init__(self):
        super().__init__(object_type="Invitation")


class AlreadyExistsQuiz(AlreadyExists):
    def __init__(self):
        super().__init__(object_type="Quiz")


class AlreadyExistsQuestion(AlreadyExists):
    def __init__(self):
        super().__init__(object_type="Question")


class ErrorCreating(CustomException):
    def __init__(self, **kwargs):
        super().__init__(detail="Error creating {object_type}: {e}", **kwargs)


class ErrorCreatingUser(ErrorCreating):
    def __init__(self, e):
        super().__init__(object_type="User", e=e)


class ErrorCreatingCompany(ErrorCreating):
    def __init__(self, e):
        super().__init__(object_type="Company", e=e)


class ErrorCreatingAccessToken(ErrorCreating):
    def __init__(self, e):
        super().__init__(object_type="Access token", e=e)


class ErrorCreatingRefreshToken(ErrorCreating):
    def __init__(self, e):
        super().__init__(object_type="Refresh token", e=e)


class ErrorCreatingUserAuth0(ErrorCreating):
    def __init__(self, e):
        super().__init__(object_type="User in auth0", e=e)


class ErrorCreatingInvitation(ErrorCreating):
    def __init__(self, e):
        super().__init__(object_type="Invitation", e=e)


class ErrorCreatingQuiz(ErrorCreating):
    def __init__(self, e):
        super().__init__(object_type="Quiz", e=e)


class ErrorCreatingQuestion(ErrorCreating):
    def __init__(self, e):
        super().__init__(object_type="Question", e=e)


class ErrorUpdating(CustomException):
    def __init__(self, **kwargs):
        super().__init__(detail="Error updating {object_type}: {e}", **kwargs)


class ErrorUpdatingUser(ErrorUpdating):
    def __init__(self, e):
        super().__init__(object_type="User", e=e)


class ErrorUpdatingCompany(ErrorUpdating):
    def __init__(self, e):
        super().__init__(object_type="Company", e=e)


class ErrorUpdatingUserProfile(ErrorUpdating):
    def __init__(self, e):
        super().__init__(object_type="User profile", e=e)


class ErrorUpdatingEmail(ErrorUpdating):
    def __init__(self):
        super().__init__(detail="User email")


class ErrorUpdatingQuiz(ErrorUpdating):
    def __init__(self, e):
        super().__init__(object_type="Quiz", e=e)


class ErrorUpdatingQuestion(ErrorUpdating):
    def __init__(self, e):
        super().__init__(object_type="Question", e=e)


class ErrorDeleting(CustomException):
    def __init__(self, **kwargs):
        super().__init__(detail="Error deleting {object_type}: {e}", **kwargs)


class ErrorDeletingUser(ErrorDeleting):
    def __init__(self, e):
        super().__init__(object_type="User", e=e)


class ErrorDeletingCompany(ErrorDeleting):
    def __init__(self, e):
        super().__init__(object_type="Company", e=e)


class ErrorDeletingUserProfile(ErrorDeleting):
    def __init__(self, e):
        super().__init__(object_type="User profile", e=e)


class ErrorDeletingAnotherProfile(ErrorDeleting):
    def __init__(self, e):
        super().__init__(object_type="Quiz", e=e)


class ErrorDeletingQuiz(ErrorDeleting):
    def __init__(self, e):
        super().__init__(object_type="Quiz", e=e)


class ErrorDeletingQuestion(ErrorDeleting):
    def __init__(self, e):
        super().__init__(object_type="Quiz", e=e)


class Invalid(CustomException):
    def __init__(self, **kwargs):
        super().__init__(detail="Invalid {object_type}, {details}", **kwargs)


class InvalidToken(Invalid):
    def __init__(self, e):
        super().__init__(object_type="Token", details=e)


class InvalidAction(Invalid):
    def __init__(self):
        super().__init__(object_type="Action", details="use 'accept' or 'reject")


class InvalidExportFormat(Invalid):
    def __init__(self):
        super().__init__(object_type="Export Format", details="supported formats: JSON, CSV.")


class ErrorSettingRole(CustomException):
    def __init__(self, **kwargs):
        super().__init__(detail="Error setting {object_type} role for User: {e}", **kwargs)


class ErrorSettingRoleAdmin(ErrorSettingRole):
    def __init__(self, e):
        super().__init__(object_type="Admin", e=e)


class Not(CustomException):
    def __init__(self, **kwargs):
        super().__init__(detail="You are not the {object_type} of this company", **kwargs)


class NotOwner(Not):
    def __init__(self):
        super().__init__(object_type="Owner")


class NotMember(Not):
    def __init__(self):
        super().__init__(object_type="Member")


class NotOwnerOrAdmin(Not):
    def __init__(self):
        super().__init__(object_type="Owner or Admin")


class NotOwnerOrAdminOrSelf(Not):
    def __init__(self):
        super().__init__(object_type="Owner or Admin or Self")


class NotSelf(Not):
    def __init__(self):
        super().__init__(object_type="Self")


class ErrorPasswordMatch(CustomException):
    def __init__(self, **kwargs):
        super().__init__(detail="Error password match.", **kwargs)


class ErrorAuthentication(CustomException):
    def __init__(self, e, **kwargs):
        super().__init__(detail=f"Error user authentication: {e}", **kwargs)


class TokenExpired(CustomException):
    def __init__(self, **kwargs):
        super().__init__(detail="Token expired", **kwargs)


class InvalidCredentials(CustomException):
    def __init__(self, **kwargs):
        super().__init__(detail="Invalid credentials", **kwargs)


class ErrorHiddenCompany(CustomException):
    def __init__(self, company_id, **kwargs):
        super().__init__(detail=f"Company with ID {company_id} is hidden", **kwargs)


class ErrorRemovingMember(CustomException):
    def __init__(self, member_id, e, **kwargs):
        super().__init__(detail=f"Error removing member {member_id}: {e}", **kwargs)


class OwnerLeave(CustomException):
    def __init__(self, **kwargs):
        super().__init__(detail="Owner cannot leave the company", **kwargs)


class ErrorLeavingCompany(CustomException):
    def __init__(self, company_id, e, **kwargs):
        super().__init__(detail=f"Error leaving company with ID {company_id}: {e}", **kwargs)


class InviteToOwnCompany(CustomException):
    def __init__(self, **kwargs):
        super().__init__(detail="You cannot invite yourself to your own company", **kwargs)


class NoPermission(CustomException):
    def __init__(self, **kwargs):
        super().__init__(detail="You don't have permission", **kwargs)


class ErrorHandleInvitation(CustomException):
    def __init__(self, e, **kwargs):
        super().__init__(detail=f"Error during handle the invitation for company: {e}", **kwargs)


class ErrorChangeOwnerAdminRole(CustomException):
    def __init__(self, **kwargs):
        super().__init__(detail="Error change admin role for owner", **kwargs)


class ErrorPassQuiz(CustomException):
    def __init__(self, e, **kwargs):
        super().__init__(detail=f"Error passing quiz: {e}", **kwargs)


class EmptyAnswer(CustomException):
    def __init__(self, **kwargs):
        super().__init__(detail="Answer is empty", **kwargs)


class LessThen2Questions(CustomException):
    def __init__(self, **kwargs):
        super().__init__(detail="There should be at least 2 questions in the quiz", **kwargs)


class LessThen2Answers(CustomException):
    def __init__(self, **kwargs):
        super().__init__(detail="There should be at least 2 answers for question", **kwargs)


class QuizNotAvailable(CustomException):
    def __init__(self, **kwargs):
        super().__init__(detail="Quiz is not available", **kwargs)


class ErrorUserResultCompany(CustomException):
    def __init__(self, company_id, e, **kwargs):
        super().__init__(detail=f"fError retrieving average scores for user in company with ID "
                                f"{company_id}: {e}", **kwargs)


class ErrorUserResultCompanies(CustomException):
    def __init__(self, e, **kwargs):
        super().__init__(detail=f"Error retrieving average scores for user in companies: {e}",**kwargs)


class ErrorCompaniesResults(CustomException):
    def __init__(self, e, **kwargs):
        super().__init__(detail=f"Error retrieving average scores for all users in companies: {e}", **kwargs)


class ErrorUsersResults(CustomException):
    def __init__(self, e, **kwargs):
        super().__init__(detail=f"Error retrieving average scores for all users: {e}", **kwargs)


class ErrorQuizResults(CustomException):
    def __init__(self, e, **kwargs):
        super().__init__(detail=f"Error retrieving quiz results for all users: {e}", **kwargs)


class ErrorGetRedisData(CustomException):
    def __init__(self, e, **kwargs):
        super().__init__(detail=f"Error retrieving redis data: {e}", **kwargs)


class ErrorExport(CustomException):
    def __init__(self, e, **kwargs):
        super().__init__(detail=f"Error exporting data: {e}", **kwargs)


class ErrorCompanyAverageScoresOverTime(CustomException):
    def __init__(self, e, **kwargs):
        super().__init__(detail=f"Error retrieving data with company average scores over time: {e}", **kwargs)


class ErrorCompanyLastAttemptTimes(CustomException):
    def __init__(self, e, **kwargs):
        super().__init__(detail=f"Error retrieving last attempt times for company: {e}", **kwargs)


class ErrorUserResultsQuizzesOverTimes(CustomException):
    def __init__(self, e, **kwargs):
        super().__init__(detail=f"Error retrieving average scores for user for all quizzes with over time: {e}", **kwargs)


class ErrorUserCompletedQuizzes(CustomException):
    def __init__(self, e, **kwargs):
        super().__init__(detail=f"Error retrieving completed quizzes for user: {e}", **kwargs)

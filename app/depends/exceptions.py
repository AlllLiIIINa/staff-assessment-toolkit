class CustomException(Exception):
    def __init__(self, status_code: int, detail: str, **kwargs):
        self.status_code = status_code
        self.detail = detail.format(**kwargs)
        super().__init__(self.detail)


class ErrorStartingApp(CustomException):
    def __init__(self, e, **kwargs):
        super().__init__(status_code=500, detail=f"Error starting app: {e}", **kwargs)


class ErrorPostgresSQL(CustomException):
    def __init__(self, e, **kwargs):
        super().__init__(status_code=500, detail=f"Error checking PostgresSQL connection: {e}", **kwargs)


class ErrorRedis(CustomException):
    def __init__(self, e, **kwargs):
        super().__init__(status_code=500, detail=f"Error checking Redis connection: {e}", **kwargs)


class ObjectNotFound(CustomException):
    def __init__(self, **kwargs):
        super().__init__(status_code=404, detail="{object_type} with ID {object_id} not found.", **kwargs)


class UserNotFound(ObjectNotFound):
    def __init__(self, user_id: str):
        super().__init__(object_type="User", object_id=user_id)


class CompanyNotFound(ObjectNotFound):
    def __init__(self, company_id: str):
        super().__init__(object_type="Company", object_id=company_id)


class InvitationNotFound(ObjectNotFound):
    def __init__(self, invitation_id: str):
        super().__init__(object_type="Invitation", object_id=invitation_id)


class ErrorRetrieving(CustomException):
    def __init__(self, **kwargs):
        super().__init__(status_code=500, detail="Error retrieving {object_type}: {e}", **kwargs)


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
        super().__init__(object_type="membership requests for User",  e=e)


class ErrorRetrievingMembershipCompany(ErrorRetrieving):
    def __init__(self, e):
        super().__init__(object_type="membership requests for Company", e=e)


class ErrorRetrievingInvitation(ErrorRetrieving):
    def __init__(self, e):
        super().__init__(object_type="invitations for User", e=e)


class ErrorRetrievingAdmin(ErrorRetrieving):
    def __init__(self, e):
        super().__init__(object_type="admins for company", e=e)


class AlreadyExists(CustomException):
    def __init__(self, **kwargs):
        super().__init__(status_code=409, detail="{object_type} already exists.", **kwargs)


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


class ErrorCreating(CustomException):
    def __init__(self, **kwargs):
        super().__init__(status_code=500, detail="Error creating {object_type}: {e}", **kwargs)


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


class ErrorUpdating(CustomException):
    def __init__(self, **kwargs):
        super().__init__(status_code=500, detail="Error updating {object_type}: {e}", **kwargs)


class ErrorUpdatingUser(ErrorUpdating):
    def __init__(self, e):
        super().__init__(object_type="User", e=e)


class ErrorUpdatingCompany(ErrorUpdating):
    def __init__(self, e):
        super().__init__(object_type="Company", e=e)


class ErrorUpdatingUserProfile(ErrorUpdating):
    def __init__(self, e):
        super().__init__(object_type="User profile", e=e)


class ErrorUpdateEmail(ErrorUpdating):
    def __init__(self, **kwargs):
        super().__init__(detail="User email", **kwargs)


class ErrorDeleting(CustomException):
    def __init__(self, **kwargs):
        super().__init__(status_code=500, detail="Error deleting {object_type}: {e}", **kwargs)


class ErrorDeletingUser(ErrorDeleting):
    def __init__(self, e):
        super().__init__(object_type="User", e=e)


class ErrorDeletingCompany(ErrorDeleting):
    def __init__(self, e):
        super().__init__(object_type="Company", e=e)


class ErrorDeletingUserProfile(ErrorDeleting):
    def __init__(self, e):
        super().__init__(object_type="User profile", e=e)


class Invalid(CustomException):
    def __init__(self, **kwargs):
        super().__init__(status_code=500, detail="Invalid {object_type}, {details}", **kwargs)


class InvalidToken(Invalid):
    def __init__(self, e):
        super().__init__(object_type="Token", details=e)


class InvalidAction(Invalid):
    def __init__(self):
        super().__init__(object_type="Action", details="use 'accept' or 'reject")


class ErrorSettingRole(CustomException):
    def __init__(self, **kwargs):
        super().__init__(status_code=500, detail="Error setting {object_type} role for User: {e}", **kwargs)


class ErrorSettingRoleAdmin(ErrorSettingRole):
    def __init__(self, e):
        super().__init__(object_type="Admin", e=e)


class ErrorPasswordMatch(CustomException):
    def __init__(self, **kwargs):
        super().__init__(status_code=401, detail="Error password match.", **kwargs)


class ErrorAuthentication(CustomException):
    def __init__(self, e, **kwargs):
        super().__init__(status_code=401, detail=f"Error user authentication: {e}", **kwargs)


class TokenExpired(CustomException):
    def __init__(self, **kwargs):
        super().__init__(status_code=201, detail="Token expired", **kwargs)


class InvalidCredentials(CustomException):
    def __init__(self, **kwargs):
        super().__init__(status_code=403, detail="Invalid credentials", **kwargs)


class ErrorDeleteAnotherProfile(CustomException):
    def __init__(self, **kwargs):
        super().__init__(status_code=403, detail="You cannot delete another user's profile", **kwargs)


class ErrorHiddenCompany(CustomException):
    def __init__(self, company_id, **kwargs):
        super().__init__(status_code=404, detail=f"Company with ID {company_id} is hidden", **kwargs)


class NotOwner(CustomException):
    def __init__(self, **kwargs):
        super().__init__(status_code=403, detail="You are not the owner of this company", **kwargs)


class ErrorRemovingMember(CustomException):
    def __init__(self, member_id, e, **kwargs):
        super().__init__(status_code=500, detail=f"Error removing member {member_id}: {e}", **kwargs)


class OwnerLeave(CustomException):
    def __init__(self, **kwargs):
        super().__init__(status_code=400, detail="Owner cannot leave the company", **kwargs)


class ErrorLeavingCompany(CustomException):
    def __init__(self, company_id, e, **kwargs):
        super().__init__(status_code=400, detail=f"Error leaving company with ID {company_id}: {e}", **kwargs)


class NotMember(CustomException):
    def __init__(self, **kwargs):
        super().__init__(status_code=404, detail="You are not a member of this company", **kwargs)


class InviteToOwnCompany(CustomException):
    def __init__(self, **kwargs):
        super().__init__(status_code=400, detail="You cannot invite yourself to your own company", **kwargs)


class NoPermission(CustomException):
    def __init__(self, **kwargs):
        super().__init__(status_code=403, detail="You don't have permission", **kwargs)


class ErrorHandleInvitation(CustomException):
    def __init__(self, e, **kwargs):
        super().__init__(status_code=500, detail=f"Error during handle the invitation for company: {e}", **kwargs)

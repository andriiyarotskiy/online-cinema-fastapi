from abc import ABC, abstractmethod


class EmailSenderInterface(ABC):

    @abstractmethod
    async def send_activation_email(self, email: str, activation_link: str) -> None:
        """
        Asynchronously send an account activation email.

        Args:
            email (str): The recipient's email address.
            activation_link (str): The activation link to include in the email.
        """
        pass

    @abstractmethod
    async def send_activation_complete_email(self, email: str, login_link: str) -> None:
        """
        Asynchronously send an email confirming that the account has been activated.

        Args:
            email (str): The recipient's email address.
            login_link (str): The login link to include in the email.
        """
        pass

    @abstractmethod
    async def send_password_reset_email(self, email: str, reset_link: str) -> None:
        """
        Asynchronously send a password reset request email.

        Args:
            email (str): The recipient's email address.
            reset_link (str): The password reset link to include in the email.
        """
        pass

    @abstractmethod
    async def send_password_reset_complete_email(
        self, email: str, login_link: str
    ) -> None:
        """
        Asynchronously send an email confirming that the password has been reset.

        Args:
            email (str): The recipient's email address.
            login_link (str): The login link to include in the email.
        """
        pass

    @abstractmethod
    async def send_comment_reply_email(
        self,
        recipient_email: str,
        sender_email: str,
        movie_id: int,
        comment_id: int,
    ) -> None:
        """
        Asynchronously send an email notification when a comment receives a reply.

        Args:
            recipient_email (str): The recipient's email address.
            sender_email (str): The email address of the user who replied.
            movie_id (int): The movie identifier.
            comment_id (int): The reply comment identifier.
        """
        pass

    @abstractmethod
    async def send_comment_like_email(
        self,
        recipient_email: str,
        sender_email: str,
        movie_name: str,
        comment_content: str,
    ) -> None:
        """
        Asynchronously send an email notification when a comment receives a like.

        Args:
            recipient_email (str): The recipient's email address.
            sender_email (str): The email address of the user who liked the comment.
            movie_name (str): The movie name.
            comment_content (str): The liked comment content.
        """
        pass

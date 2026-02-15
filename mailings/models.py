from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class Recipient(models.Model):
    """Получатель рассылки"""
    email = models.EmailField(unique=True, verbose_name='Email')
    full_name = models.CharField(max_length=255, verbose_name='Ф.И.О.')
    comment = models.TextField(blank=True, verbose_name='Комментарий')

    class Meta:
        verbose_name = 'Получатель'
        verbose_name_plural = 'Получатели'

    def __str__(self):
        return f'{self.full_name} ({self.email})'


class Message(models.Model):
    """Сообщение для рассылки"""
    subject = models.CharField(max_length=255, verbose_name='Тема письма')
    body = models.TextField(verbose_name='Тело письма')

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    """Рассылка"""
    STATUS_CHOICES = [
        ('Создана', 'Создана'),
        ('Запущена', 'Запущена'),
        ('Завершена', 'Завершена'),
    ]

    start_time = models.DateTimeField(verbose_name='Дата и время начала отправки')
    end_time = models.DateTimeField(verbose_name='Дата и время окончания отправки')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Создана', verbose_name='Статус')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name='Сообщение')
    recipients = models.ManyToManyField(Recipient, verbose_name='Получатели')

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'

    def __str__(self):
        return f'Рассылка {self.id} - {self.get_current_status()}'

    def clean(self):
        """Валидация полей модели"""
        super().clean()

        if self.start_time and self.end_time:
            # start_time должен быть раньше end_time
            if self.start_time >= self.end_time:
                raise ValidationError({
                    'end_time': 'Дата окончания должна быть позже даты начала.'
                })

            # start_time не может быть в прошлом (только при создании)
            if not self.pk and self.start_time < timezone.now():
                raise ValidationError({
                    'start_time': 'Дата начала не может быть в прошлом.'
                })

    def get_current_status(self):
        """Вычисление текущего статуса рассылки динамически"""
        now = timezone.now()

        if now > self.end_time:
            return 'Завершена'
        elif now >= self.start_time:
            return 'Запущена'
        else:
            return 'Создана'

    def update_status(self):
        """Обновление статуса рассылки в базе данных"""
        new_status = self.get_current_status()
        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=['status'])

    def can_send(self):
        """Проверка, можно ли отправлять рассылку сейчас"""
        now = timezone.now()
        return self.start_time <= now <= self.end_time


class MailingAttempt(models.Model):
    """Попытка рассылки"""
    STATUS_CHOICES = [
        ('Успешно', 'Успешно'),
        ('Не успешно', 'Не успешно'),
    ]

    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name='attempts', verbose_name='Рассылка')
    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время попытки')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name='Статус')
    server_response = models.TextField(blank=True, verbose_name='Ответ почтового сервера')

    class Meta:
        verbose_name = 'Попытка рассылки'
        verbose_name_plural = 'Попытки рассылок'
        ordering = ['-attempt_time']

    def __str__(self):
        return f'Попытка {self.id} - {self.status}'

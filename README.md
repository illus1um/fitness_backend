Но чтобы полностью “одолжить” её под CRUD-функции и ORM, рекомендую добавить пару мелочей:

Внешний ключ

sql
Копировать
Редактировать
ALTER TABLE training_progress
  ADD CONSTRAINT fk_progress_user
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE;
Это гарантирует, что прогресс всегда привязан к существующему юзеру и автоматически удаляется, когда вы удаляете учётку.

Уникальный индекс для апсерта (чтобы в одном дне и на одном упражнении была ровно одна запись):

sql
Копировать
Редактировать
CREATE UNIQUE INDEX uq_progress_user_day_ex
  ON training_progress(user_id, day_index, exercise_id);
(Опционально) Индекс по user_id, чтобы запросы WHERE user_id = ... шли быстрее:

sql
Копировать
Редактировать
CREATE INDEX ix_progress_user 
  ON training_progress(user_id);
Если вы используете Alembic для миграций, то вместо ручных ALTER TABLE конкретно пропишите эти изменения в новой ревизии и выполните alembic upgrade head.

После этого ваша схема будет максимально надёжной и готовой к использованию в CRUD-операциях FastAPI + SQLAlchemy.
# �g�p����x�[�X�C���[�W
FROM python:3.10-slim

# ��ƃf�B���N�g����ݒ�
WORKDIR /app

# requirements.txt���R���e�i�ɃR�s�[
COPY requirements.txt .

# �K�v�ȃp�b�P�[�W���C���X�g�[��
RUN pip install --no-cache-dir -r requirements.txt

# �A�v���P�[�V�����̃R�[�h���R���e�i�ɃR�s�[
COPY . .

# �R�[�h�����s
CMD ["python", "main.py"]

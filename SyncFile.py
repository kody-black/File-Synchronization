from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QFileDialog, QTextEdit
from PyQt5.QtGui import QIcon
import shutil
import os
import sys
import ctypes

class SyncFilesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("./icon.ico"))
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

        # 创建文本标签和文本框
        self.src_label = QLabel("源文件夹路径:", self)
        self.src_edit = QLineEdit(self)
        self.src_button = QPushButton("选择文件夹", self)
        self.dst_label = QLabel("目标文件夹路径:", self)
        self.dst_edit = QLineEdit(self)
        self.dst_button = QPushButton("选择文件夹", self)

        # 创建文本框
        self.log_edit = QTextEdit(self)

        # 创建按钮
        self.sync_button = QPushButton("同步文件", self)

        # 设置布局
        self.src_label.move(10, 10)
        self.src_edit.move(130, 10)
        self.src_button.move(315, 10)
        self.dst_label.move(10, 40)
        self.dst_edit.move(130, 40)
        self.dst_button.move(315, 40)
        self.log_edit.setGeometry(10, 70, 400, 150)
        self.sync_button.move(160, 230)

        # 连接按钮的点击事件和处理函数
        self.src_button.clicked.connect(self.select_src_dir)
        self.dst_button.clicked.connect(self.select_dst_dir)
        self.sync_button.clicked.connect(self.sync_files)

        # 设置窗口的属性
        self.setGeometry(300, 300, 420, 270)
        self.setWindowTitle('文件夹同步工具')

        self.infomation()

    def select_src_dir(self):
        # 调用 QFileDialog.getExistingDirectory() 函数弹出文件夹选择对话框
        src_dir = QFileDialog.getExistingDirectory(self, "选择源文件夹")
        # 如果用户选择了文件夹，则在文本框中显示文件夹路径
        if src_dir:
            self.src_edit.setText(src_dir)

    def select_dst_dir(self):
        # 调用 QFileDialog.getExistingDirectory() 函数弹出文件夹选择对话框
        dst_dir = QFileDialog.getExistingDirectory(self, "选择目标文件夹")
        # 如果用户选择了文件夹，则在文本框中显示文件夹路径
        if dst_dir:
            self.dst_edit.setText(dst_dir)

    def infomation(self):
        self.log_edit.append('<font color=\"#d83b01\"><b>注意：</b></font>'+'<p>'+
        '本软件的作用是把源文件夹的内容同步到目标文件夹中'+'<p>'+
        '程序会遍历源文件夹，把相对于目标文件夹不同的地方（包括修改和添加的文件）复制到目标文件夹（其中修改过的文件会覆盖掉目标文件）'+'<p>'+
        '<font color=\"#0078d4\"><b>目标文件夹不允许是源文件夹的子文件夹</b></font>')

    def sync_files(self):
        # 获取文本框中的路径
        src_dir = self.src_edit.text()
        dst_dir = self.dst_edit.text()

        self.log_edit.clear()

        if not os.path.exists(src_dir):
            QMessageBox.warning(self, "错误", "源文件夹不存在！")
            return

        if not os.path.exists(dst_dir):
            QMessageBox.warning(self, "错误", "目标文件夹不存在！")
            return
        
        # 递归同步文件夹和文件
        def sync_files(src_dir, dst_dir) -> int:

            # 如果目标文件夹不存在，则创建目标文件夹
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            
            # 遍历源文件夹中的文件
            for src_path in os.listdir(src_dir):
                src_path = os.path.join(src_dir, src_path)
                dst_path = os.path.join(dst_dir, src_path.split(os.sep)[-1])

                # 如果是文件夹，则递归处理
                if os.path.isdir(src_path):
                    sync_files(src_path, dst_path)
                # 如果是文件，则复制文件
                else:
                    # 如果文件已经存在，则比较时间戳
                    if os.path.exists(dst_path):
                        # 获取文件的时间戳
                        src_mtime = os.path.getmtime(src_path)
                        dst_mtime = os.path.getmtime(dst_path)

                        # 如果源文件的时间戳更新，则复制文件
                        if src_mtime > dst_mtime:
                            self.log_edit.append("正在复制文件: " + src_path)
                            shutil.copy2(src_path, dst_path)
                    else:
                        # 将文件复制到目标文件夹
                        self.log_edit.append("正在复制文件: " + src_path)
                        shutil.copy2(src_path, dst_path)
            return 1

        # 调用递归函数同步文件
        if sync_files(src_dir, dst_dir):
            QMessageBox.information(self, "提示", "文件同步成功！")
        else:
            QMessageBox.critical(self, "错误", "文件同步失败！")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SyncFilesWindow()
    window.show()
    sys.exit(app.exec_())

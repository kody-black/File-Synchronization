from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QPushButton, QMessageBox, QFileDialog, QTextEdit, QHBoxLayout, QVBoxLayout, QWhatsThis
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QEvent
import shutil
import os
import sys
import ctypes

class SyncFilesWindow(QDialog):
    def __init__(self):
        super().__init__()
        filename = self.resource_path(os.path.join("ico","icon.ico"))
        icon = QIcon()
        icon.addPixmap(QPixmap(filename), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

        # 创建文本标签和文本框
        self.src_label = QLabel("源文件夹路径:", self)
        self.src_edit = QLineEdit(self)
        self.src_button = QPushButton("选择文件夹", self)
        self.dst_label = QLabel("目标文件夹路径:", self)
        self.dst_edit = QLineEdit(self)
        self.dst_button = QPushButton("选择文件夹", self)

        # 创建文本框用于显示同步的文件名称
        self.log_edit = QTextEdit(self)

        # 创建按钮
        self.sync_button = QPushButton("同步文件", self)

        # 创建水平布局，用于放置文本框和按钮
        hbox_src = QHBoxLayout()
        hbox_src.addWidget(self.src_edit)
        hbox_src.addWidget(self.src_button)
        hbox_dst = QHBoxLayout()
        hbox_dst.addWidget(self.dst_edit)
        hbox_dst.addWidget(self.dst_button)

        # 创建垂直布局
        vbox = QVBoxLayout()
        vbox.addWidget(self.src_label)
        vbox.addLayout(hbox_src)
        vbox.addWidget(self.dst_label)
        vbox.addLayout(hbox_dst)
        vbox.addWidget(self.sync_button)
        vbox.addWidget(self.log_edit)

        # 设置布局
        self.setLayout(vbox)

        # 连接按钮的点击事件和处理函数
        self.src_button.clicked.connect(self.select_src_dir)
        self.dst_button.clicked.connect(self.select_dst_dir)
        self.sync_button.clicked.connect(self.sync_files)

        # 设置窗口的属性
        self.setGeometry(300, 300, 420, 420)
        self.setWindowTitle('文件夹同步工具')

        self.infomation()

    def event(self, event):
        if event.type()==QEvent.EnterWhatsThisMode:
            QWhatsThis.leaveWhatsThisMode()
            QMessageBox.information(self, "关于", "开发：Kody Black\n"+
            "github.com/distiny-cool/File-Synchronization")
        return QDialog.event(self,event)


    def resource_path(self, relative_path):
        if getattr(sys, 'frozen', False): 
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

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
        self.log_edit.append('<font color="#0078d4"><b>功能介绍：</b></font>'+'<p>'+
        '本软件会把源文件夹和目标文件夹中不同的内容复制到目标文件夹里，完全相同的文件则直接跳过，以节省你的复制时间'+'<p>'+
        '<font color="#d83b01"><b>注意：</b></font><ul><li>目标文件夹不允许是源文件夹的子文件夹</li>'+
        '<li>如果有相同的文件，则在目标文件夹中会保留最近修改过的文件</li></ul>'+
        '<p style="text-align: right;"><font color="#6e9bc5">'+'<b> by:Kody </b></font></p>')

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

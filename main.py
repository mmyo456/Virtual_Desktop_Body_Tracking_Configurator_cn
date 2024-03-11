from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QCheckBox, QGridLayout, QComboBox, QDoubleSpinBox, QTabWidget, QSpacerItem, QSizePolicy, QMessageBox, QStackedWidget
import json
import qdarktheme
import os
from iobt_options import default_enabled, default_offsets, default_toggles, default_misc, temp_offsets, tooltips_enabled
import subprocess
import psutil


def process_exists(process_name):
    call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
    # use buildin check_output right away
    try:
        output = subprocess.check_output(call).decode(errors='ignore')
    except UnicodeDecodeError:
        output = subprocess.check_output(call).decode('cp1252', errors='ignore')  # Windows specific encoding
    # check in last line for process name
    last_line = output.strip().split('\r\n')[-1]
    # because Fail message could be translated
    return last_line.lower().startswith(process_name.lower())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Virtual Desktop虚拟Tracker配置器 Github:mmyo456")
        
        if "vrserver.exe" in (p.name() for p in psutil.process_iter()):
            dlg2 = QMessageBox()
            dlg2.setWindowTitle("Virtual Desktop虚拟Tracker配置器 Github:mmyo456")            
            dlg2.setText("错误!\n\nvrserver.exe 正在运行！\n\n请关闭 SteamVR 再试一次")

            dlg2.exec()

            if QMessageBox.StandardButton.Ok:
                exit()
        
        self.steam = ""
        try:
            with open(f"{os.getenv('LOCALAPPDATA')}\\openvr\\openvrpaths.vrpath", "r", encoding="utf-8") as file:
                self.steam = json.load(file)["config"][0].replace("\\", "/")
        except Exception as e:
            dlg2 = QMessageBox()
            dlg2.setWindowTitle("Virtual Desktop虚拟Tracker配置器")            
            dlg2.setText(f"错误：{e}")
            dlg2.exec()
            if QMessageBox.StandardButton.Ok:
                exit()
        
        self.checkboxes = {}
        self.offsets = {}   
        self.misc = {}
        self.stackedwidgets = {}
        
        layoutTab1 = QGridLayout()
        self.layoutTab2 = QGridLayout()
        self.layoutTab2.setColumnMinimumWidth(1,150)
        layoutTab3 = QVBoxLayout()


        for variable in default_toggles:
            button = QCheckBox(variable.replace("_", " ").title())
            button.setCheckable(True)
            button.setChecked(default_toggles.get(variable))     
            self.misc[variable] = button      
            
            layoutTab3.addWidget(button)
            
            
        for variable in default_misc:
            box = QDoubleSpinBox()
            box.setPrefix(f"{variable.replace('_', ' ').title()}: ")
            box.setMinimum(0)
            box.setMaximum(1)
            box.setSingleStep(0.05)
            box.setDecimals(3)
            box.setValue(default_misc[variable])            
            self.misc[variable] = box

            layoutTab3.addWidget(box)      

        spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        spacer2 = QSpacerItem(100, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        spacer3 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        
        layoutTab1.addItem(spacer, 16, 0)
        layoutTab1.addItem(spacer3,1,0)
        self.layoutTab2.addItem(spacer2,0, 1)
        
        self.upperWithHip = QPushButton("上半身（带臀部）")
        self.upperWithHip.clicked.connect(self.Upper_With_Hip_clicked)
        layoutTab1.addWidget(self.upperWithHip, 0, 0)
        
        self.upper = QPushButton("仅上半身")
        self.upper.clicked.connect(self.upper_only_clicked)
        layoutTab1.addWidget(self.upper, 0, 1)
        
        self.elbows = QPushButton("仅肘部")
        self.elbows.clicked.connect(self.elbows_only_clicked)
        layoutTab1.addWidget(self.elbows, 0, 2)
        
        self.defaults = QPushButton("重置已启用追踪器为默认设置")
        self.defaults.clicked.connect(self.reset_clicked)
        layoutTab1.addWidget(self.defaults, 17, 0)

        self.load = QPushButton("加载当前设置")
        self.load.clicked.connect(self.load_settings_clicked)
        layoutTab1.addWidget(self.load, 17, 1)

        self.load2 = QPushButton("加载当前设置")
        self.load2.clicked.connect(self.load_settings_clicked)
        self.layoutTab2.addWidget(self.load2, 4, 0)

        self.load3 = QPushButton("加载当前设置")
        self.load3.clicked.connect(self.load_settings_clicked)
        layoutTab3.addWidget(self.load3)
        
        self.export = QPushButton("应用设置（所有页面）")
        self.export.setStyleSheet("QPushButton {background-color: rgb(0,200,0); color: black} QPushButton:hover {background-color: rgb(0,200,150)}")
        self.export.clicked.connect(self.export_clicked)
        layoutTab1.addWidget(self.export, 17, 2)
        
        self.export2 = QPushButton("应用设置（所有页面）")
        self.export2.setStyleSheet("QPushButton {background-color: rgb(0,200,0); color: black} QPushButton:hover {background-color: rgb(0,200,150)}")
        self.export2.clicked.connect(self.export_clicked)
        self.layoutTab2.addWidget(self.export2, 5, 0)
        
        self.export3 = QPushButton("应用设置（所有页面）")
        self.export3.setStyleSheet("QPushButton {background-color: rgb(0,200,0); color: black} QPushButton:hover {background-color: rgb(0,200,150)}")
        self.export3.clicked.connect(self.export_clicked)
        layoutTab3.addWidget(self.export3, 10)
        
        self.loadRecommended = QCheckBox("应用推荐偏移\n（不覆盖自定义偏移）")
        self.loadRecommended.setChecked(True)
        self.loadRecommended.clicked.connect(self.checkbox_interacted)
        self.layoutTab2.addWidget(self.loadRecommended, 3, 0)
        
        first = 0
        row = 3
        column = 0
        for variable in default_enabled:
            Chinese = (variable[:-8].replace("_", " ").title())
            Chinese = (Chinese.replace("Joint", " 关节点"))
            Chinese = (Chinese.replace("Left", "左"))
            Chinese = (Chinese.replace("Right", "右"))
            Chinese = (Chinese.replace("Upper", "上侧"))
            Chinese = (Chinese.replace("Middle", "中部"))
            Chinese = (Chinese.replace("Lower", "下侧"))
            Chinese = (Chinese.replace("Head", "头部"))
            Chinese = (Chinese.replace("Neck", "颈部"))
            Chinese = (Chinese.replace("Chest", "胸部"))
            Chinese = (Chinese.replace("Spine", "脊柱"))
            Chinese = (Chinese.replace("Hips", "臀部"))
            Chinese = (Chinese.replace("Shoulder", "肩"))
            Chinese = (Chinese.replace("Scapula", "肩胛骨"))
            Chinese = (Chinese.replace("Arm", "手臂"))
            Chinese = (Chinese.replace("Wrist", "腕"))
            Chinese = (Chinese.replace("Twist", "扭转"))
            Chinese = (Chinese.replace("Hand", "手"))
            Chinese = (Chinese.replace("Leg", "腿"))
            Chinese = (Chinese.replace("Ankle", "踝"))
            Chinese = (Chinese.replace("Foot", "脚"))
            Chinese = (Chinese.replace("Subtalar", "底面"))
            Chinese = (Chinese.replace("Transverse", "横向"))
            Chinese = (Chinese.replace("Ball", "球节"))
            Chinese = (Chinese.replace(" ", ""))
            button = QCheckBox(Chinese)
            button.setCheckable(True)
            button.setChecked(default_enabled.get(variable))
            button.setToolTip(tooltips_enabled[variable])
            button.clicked.connect(lambda checked, b=button: self.checkbox_interacted(b))
            self.checkboxes[variable] = button
            layoutTab1.addWidget(button, row, column)
            row += 1
            first += 1
            if row >= 16 or first == 7:
                row = 3
                column += 1
                
        widgetTab1 = QWidget()
        widgetTab1.setLayout(layoutTab1)
            
        self.dropdown = QComboBox()
            
        for axis in ["平移 X", "平移 Y", "平移 Z", "旋转 X", "旋转 Y", "旋转 Z"]:
            self.stackedwidgets[axis] = QStackedWidget()

        row = 0
        column = 0
        for variable in default_enabled:        
            self.dropdown.addItem(variable[:-8].replace("_", " ").title())
            self.offsets[variable] = {}
            for axis in ["平移 X", "平移 Y", "平移 Z", "旋转 X", "旋转 Y", "旋转 Z"]:
                box = QDoubleSpinBox()
                box.setPrefix(f"{axis}: ")
                if axis[:-2] == "旋转":
                    box.setMaximum(360)
                    box.setMinimum(-360)
                    box.setSingleStep(90)
                    try:
                        box.setValue(default_offsets[f"{variable[:-8]}_rot_{axis[-1].lower()}"])
                    except:
                        ()
                else:
                    box.setSingleStep(0.01)
                    box.setMaximum(1)
                    box.setMinimum(-1)
                    box.setDecimals(3)                    
                self.offsets[variable][axis] = box
                self.stackedwidgets[axis].addWidget(box)
                row += 1
                if row >= 9:
                    row = 0
                    column += 1

        self.layoutTab2.addWidget(self.dropdown, 2, 0)
        
        i=1
        for axis in ["平移 X", "平移 Y", "平移 Z", "旋转 X", "旋转 Y", "旋转 Z"]:
            self.layoutTab2.addWidget(self.stackedwidgets[axis], i, 2)
            i+=1
        self.dropdown.currentIndexChanged.connect(self.offset_index_changed)

        widgetTab2 = QWidget()
        widgetTab2.setLayout(self.layoutTab2)
        
        widgetTab3 = QWidget()
        widgetTab3.setLayout(layoutTab3)

        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.North)
        tabs.setMovable(True)

        tabs.addTab(widgetTab1, "启用追踪器")
        tabs.addTab(widgetTab2, "追踪器偏移")
        tabs.addTab(widgetTab3, "其他设置")

        self.setCentralWidget(tabs)
          
    def offset_index_changed(self, index):
        i=1
        for axis in ["平移 X", "平移 Y", "平移 Z", "旋转 X", "旋转 Y", "旋转 Z"]:
            self.stackedwidgets[axis].setCurrentIndex(index)
            i+=1
                
    def checkbox_interacted(self, checkbox):
        ()
     
    def reset_clicked(self):
        for variable, checkbox in self.checkboxes.items():
            default_state = default_enabled.get(variable, False)
            checkbox.setChecked(default_state)
        
    def Upper_With_Hip_clicked(self):
        for variable, checkbox in self.checkboxes.items():
            if variable == "left_arm_upper_joint_enabled" or variable == "left_arm_lower_joint_enabled" or variable == "right_arm_upper_joint_enabled" or variable == "right_arm_lower_joint_enabled" or variable == "chest_joint_enabled" or variable == "hips_joint_enabled":
                checkbox.setChecked(True)
            else:
                checkbox.setChecked(False) 

    def upper_only_clicked(self):
        for variable, checkbox in self.checkboxes.items():
            if variable == "left_arm_upper_joint_enabled" or variable == "left_arm_lower_joint_enabled" or variable == "right_arm_upper_joint_enabled" or variable == "right_arm_lower_joint_enabled" or variable == "chest_joint_enabled":
                checkbox.setChecked(True)
            else:
                checkbox.setChecked(False)
        
    def elbows_only_clicked(self):
        for variable, checkbox in self.checkboxes.items():
            if variable == "left_arm_upper_joint_enabled" or variable == "left_arm_lower_joint_enabled" or variable == "right_arm_upper_joint_enabled" or variable == "right_arm_lower_joint_enabled":
                checkbox.setChecked(True)
            else:
                checkbox.setChecked(False) 

    def load_settings_clicked(self):
        try:
            with open(f"{self.steam}/steamvr.vrsettings", "r", encoding="utf-8") as file:
                current = json.load(file)["driver_VirtualDesktop"]                  
                
                for variable in default_enabled:
                    try:
                        self.checkboxes[variable].setChecked(current[variable])
                    except:
                        ()
                    
                for variable in default_enabled:
                    for axis in ["平移 X", "平移 Y", "平移 Z", "旋转 X", "旋转 Y", "旋转 Z"]:
                        try:                
                            if axis[:-2] == "旋转":
                                self.offsets[variable][axis].setValue(current[f"{variable[:-8]}_rot_{axis[-1].lower()}"])
                            else:
                                self.offsets[variable][axis].setValue(current[f"{variable[:-8]}_offset_{axis[-1].lower()}"])
                        except:
                            ()

                for variable in default_misc:
                    try:
                        self.misc[variable].setValue(current[variable])
                    except:
                        ()

                for variable in default_toggles:
                    try:
                        self.misc[variable].setChecked(current[variable])
                    except:
                        ()
            
        except Exception as e:
            if str(e) == r"'driver_VirtualDesktop'":
                ()
            else:
                dlg2 = QMessageBox()
                dlg2.setWindowTitle("Virtual Desktop虚拟Tracker配置器 mmyo456")            
                dlg2.setText(f"错误：{e}")
                dlg2.exec()
                if QMessageBox.StandardButton.Ok:
                    exit()
        
    def export_clicked(self):
        if "vrserver.exe" in (p.name() for p in psutil.process_iter()):
            dlg2 = QMessageBox()
            dlg2.setWindowTitle("Virtual Desktop虚拟Tracker配置器 Github:mmyo456")            
            dlg2.setText("错误!\n\nvrserver.exe 正在运行！\n\n请关闭 SteamVR 再试一次")

            dlg2.exec()

            if QMessageBox.StandardButton.Ok:
                exit()
        
        export_dict = {}

        if self.loadRecommended.isChecked():
            for variable in temp_offsets:
                export_dict[variable] = temp_offsets[variable]
                
        for variable, checkbox in self.checkboxes.items():
           if default_enabled[variable] != checkbox.isChecked():
                export_dict[variable] = checkbox.isChecked()
           
        for variable, joint in self.offsets.items():
            for axis, box in joint.items():
                if axis[:-2] == "旋转":
                    try:
                        if abs(box.value() - default_offsets[f"{variable[:-8]}_rot_{axis[-1].lower()}"]) < 0.001:
                            ()
                        else:
                            export_dict[f"{variable[:-8]}_rot_{axis[-1].lower()}"] = box.value()
                    except:
                        if box.value() >= 0.001:
                            export_dict[f"{variable[:-8]}_rot_{axis[-1].lower()}"] = box.value()
                else:
                    try:
                        if abs(box.value() - default_offsets[f"{variable[:-8]}_offset_{axis[-1].lower()}"]) < 0.001:
                            ()
                        else:
                            export_dict[f"{variable[:-8]}_offset_{axis[-1].lower()}"] = box.value()
                    except:
                        if box.value() >= 0.001:
                            export_dict[f"{variable[:-8]}_offset_{axis[-1].lower()}"] = box.value()

        for variable, input in self.misc.items():
            try:
                if abs(default_misc[variable] - input.value()) >= 0.001:
                    export_dict[variable] = input.value()
            except:
                ()
            try:
                if default_toggles[variable] != input.isChecked():
                    export_dict[variable] = input.isChecked()
            except:
                ()
           
        try:   
            with open(f"{self.steam}/steamvr.vrsettings", "r+", encoding="utf-8") as settings:
                
                temp = json.load(settings)
                try:
                    with open(f"{self.steam}/steamvr.vrsettings.originalbackup", "x", encoding="utf-8") as backup:
                        json.dump(temp, fp=backup)
                        backup.close()
                except:
                    ()
                
                try:
                    with open(f"{self.steam}/steamvr.vrsettings.lastbackup", "w") as backup:
                        json.dump(temp, fp=backup)
                        backup.close()
                except:
                    ()
                
                temp["driver_VirtualDesktop"] = export_dict
                settings.seek(0)
                json.dump(temp, indent=3, fp=settings)
                settings.truncate()
                settings.close()
                
                dlg = QMessageBox(self)
                dlg.setWindowTitle("Virtual Desktop虚拟Tracker配置器")            
                dlg.setText(f"成功导出到 SteamVR！\n\n原始设置备份保存在：{self.steam}/steamvr.vrsettings.originalbackup\n\n之前设置的备份保存在： {self.steam}/steamvr.vrsettings.lastbackup")
                dlg.exec()
                if QMessageBox.StandardButton.Ok:
                    app.exit()

        except Exception as e:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Virtual Desktop虚拟Tracker配置器")            
            dlg.setText(f"错误：{e}")
            dlg.exec()
            if QMessageBox.StandardButton.Ok:
                app.exit()

app = QApplication([])

qdarktheme.setup_theme(additional_qss="QToolTip { border: 0px; }")

window = MainWindow()
window.show()

app.exec()

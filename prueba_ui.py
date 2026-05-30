# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'prueba.ui'
##
## Created by: Qt User Interface Compiler version 6.11.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QButtonGroup, QFrame, QGridLayout,
    QHBoxLayout, QLabel, QLayout, QMainWindow,
    QMenuBar, QProgressBar, QPushButton, QScrollArea,
    QSizePolicy, QSlider, QSpacerItem, QStackedWidget,
    QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1032, 725)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QSize(480, 360))
        MainWindow.setMaximumSize(QSize(1920, 1080))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.horizontalLayout_2 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.videoLabel = QLabel(self.centralwidget)
        self.videoLabel.setObjectName(u"videoLabel")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.videoLabel.sizePolicy().hasHeightForWidth())
        self.videoLabel.setSizePolicy(sizePolicy1)
        self.videoLabel.setFrameShape(QFrame.Shape.StyledPanel)
        self.videoLabel.setFrameShadow(QFrame.Shadow.Sunken)
        self.videoLabel.setScaledContents(True)
        self.videoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_3.addWidget(self.videoLabel)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.verticalLayout_3.setStretch(0, 1)
        self.verticalLayout_3.setStretch(1, 3)

        self.verticalLayout_2.addLayout(self.verticalLayout_3)

        self.verticalLayout_2.setStretch(0, 3)

        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.pipButton = QPushButton(self.centralwidget)
        self.pipButton.setObjectName(u"pipButton")

        self.horizontalLayout_3.addWidget(self.pipButton)

        self.stopButton = QPushButton(self.centralwidget)
        self.stopButton.setObjectName(u"stopButton")
        self.stopButton.setIconSize(QSize(27, 16))

        self.horizontalLayout_3.addWidget(self.stopButton)

        self.pushButton_3 = QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.pushButton_3)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        sizePolicy.setHeightForWidth(self.stackedWidget.sizePolicy().hasHeightForWidth())
        self.stackedWidget.setSizePolicy(sizePolicy)
        self.mainPage = QWidget()
        self.mainPage.setObjectName(u"mainPage")
        sizePolicy.setHeightForWidth(self.mainPage.sizePolicy().hasHeightForWidth())
        self.mainPage.setSizePolicy(sizePolicy)
        self.verticalLayout_5 = QVBoxLayout(self.mainPage)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.pushButton_4 = QPushButton(self.mainPage)
        self.pushButton_4.setObjectName(u"pushButton_4")
        self.pushButton_4.setEnabled(False)
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.pushButton_4.sizePolicy().hasHeightForWidth())
        self.pushButton_4.setSizePolicy(sizePolicy2)

        self.gridLayout_2.addWidget(self.pushButton_4, 0, 2, 1, 1)

        self.changeControlsButton = QPushButton(self.mainPage)
        self.changeControlsButton.setObjectName(u"changeControlsButton")
        sizePolicy2.setHeightForWidth(self.changeControlsButton.sizePolicy().hasHeightForWidth())
        self.changeControlsButton.setSizePolicy(sizePolicy2)

        self.gridLayout_2.addWidget(self.changeControlsButton, 0, 0, 1, 1)

        self.gamesButton = QPushButton(self.mainPage)
        self.gamesButton.setObjectName(u"gamesButton")
        sizePolicy2.setHeightForWidth(self.gamesButton.sizePolicy().hasHeightForWidth())
        self.gamesButton.setSizePolicy(sizePolicy2)

        self.gridLayout_2.addWidget(self.gamesButton, 0, 1, 1, 1)

        self.pushButton_5 = QPushButton(self.mainPage)
        self.pushButton_5.setObjectName(u"pushButton_5")
        self.pushButton_5.setEnabled(False)
        sizePolicy2.setHeightForWidth(self.pushButton_5.sizePolicy().hasHeightForWidth())
        self.pushButton_5.setSizePolicy(sizePolicy2)

        self.gridLayout_2.addWidget(self.pushButton_5, 1, 0, 1, 1)


        self.verticalLayout_5.addLayout(self.gridLayout_2)

        self.stackedWidget.addWidget(self.mainPage)
        self.gesturesPage = QWidget()
        self.gesturesPage.setObjectName(u"gesturesPage")
        self.verticalLayout_7 = QVBoxLayout(self.gesturesPage)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(-1, -1, 9, -1)
        self.gesturesBackButton = QPushButton(self.gesturesPage)
        self.gesturesBackButton.setObjectName(u"gesturesBackButton")
        sizePolicy2.setHeightForWidth(self.gesturesBackButton.sizePolicy().hasHeightForWidth())
        self.gesturesBackButton.setSizePolicy(sizePolicy2)

        self.horizontalLayout_5.addWidget(self.gesturesBackButton)

        self.gesturesSaveLocalButton = QPushButton(self.gesturesPage)
        self.gesturesSaveLocalButton.setObjectName(u"gesturesSaveLocalButton")
        sizePolicy2.setHeightForWidth(self.gesturesSaveLocalButton.sizePolicy().hasHeightForWidth())
        self.gesturesSaveLocalButton.setSizePolicy(sizePolicy2)

        self.horizontalLayout_5.addWidget(self.gesturesSaveLocalButton)

        self.gesturesLoadButton = QPushButton(self.gesturesPage)
        self.gesturesLoadButton.setObjectName(u"gesturesLoadButton")
        sizePolicy2.setHeightForWidth(self.gesturesLoadButton.sizePolicy().hasHeightForWidth())
        self.gesturesLoadButton.setSizePolicy(sizePolicy2)

        self.horizontalLayout_5.addWidget(self.gesturesLoadButton)

        self.gesturesSaveExternalButton = QPushButton(self.gesturesPage)
        self.gesturesSaveExternalButton.setObjectName(u"gesturesSaveExternalButton")
        sizePolicy2.setHeightForWidth(self.gesturesSaveExternalButton.sizePolicy().hasHeightForWidth())
        self.gesturesSaveExternalButton.setSizePolicy(sizePolicy2)

        self.horizontalLayout_5.addWidget(self.gesturesSaveExternalButton)

        self.horizontalLayout_5.setStretch(0, 1)
        self.horizontalLayout_5.setStretch(1, 1)
        self.horizontalLayout_5.setStretch(2, 1)
        self.horizontalLayout_5.setStretch(3, 1)

        self.verticalLayout_7.addLayout(self.horizontalLayout_5)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.pushButton_22 = QPushButton(self.gesturesPage)
        self.gestureButtons = QButtonGroup(MainWindow)
        self.gestureButtons.setObjectName(u"gestureButtons")
        self.gestureButtons.addButton(self.pushButton_22)
        self.pushButton_22.setObjectName(u"pushButton_22")
        sizePolicy2.setHeightForWidth(self.pushButton_22.sizePolicy().hasHeightForWidth())
        self.pushButton_22.setSizePolicy(sizePolicy2)
        self.pushButton_22.setCheckable(False)
        self.pushButton_22.setAutoExclusive(True)

        self.gridLayout.addWidget(self.pushButton_22, 1, 1, 1, 1)

        self.pushButton_18 = QPushButton(self.gesturesPage)
        self.gestureButtons.addButton(self.pushButton_18)
        self.pushButton_18.setObjectName(u"pushButton_18")
        sizePolicy2.setHeightForWidth(self.pushButton_18.sizePolicy().hasHeightForWidth())
        self.pushButton_18.setSizePolicy(sizePolicy2)
        self.pushButton_18.setIconSize(QSize(16, 16))
        self.pushButton_18.setCheckable(False)
        self.pushButton_18.setAutoExclusive(True)

        self.gridLayout.addWidget(self.pushButton_18, 0, 0, 1, 1)

        self.pushButton_19 = QPushButton(self.gesturesPage)
        self.gestureButtons.addButton(self.pushButton_19)
        self.pushButton_19.setObjectName(u"pushButton_19")
        sizePolicy2.setHeightForWidth(self.pushButton_19.sizePolicy().hasHeightForWidth())
        self.pushButton_19.setSizePolicy(sizePolicy2)
        self.pushButton_19.setIconSize(QSize(16, 16))
        self.pushButton_19.setCheckable(False)
        self.pushButton_19.setAutoExclusive(True)

        self.gridLayout.addWidget(self.pushButton_19, 1, 0, 1, 1)

        self.pushButton_21 = QPushButton(self.gesturesPage)
        self.gestureButtons.addButton(self.pushButton_21)
        self.pushButton_21.setObjectName(u"pushButton_21")
        sizePolicy2.setHeightForWidth(self.pushButton_21.sizePolicy().hasHeightForWidth())
        self.pushButton_21.setSizePolicy(sizePolicy2)
        self.pushButton_21.setIconSize(QSize(16, 16))
        self.pushButton_21.setCheckable(False)
        self.pushButton_21.setAutoExclusive(True)

        self.gridLayout.addWidget(self.pushButton_21, 0, 2, 1, 1)

        self.pushButton_20 = QPushButton(self.gesturesPage)
        self.gestureButtons.addButton(self.pushButton_20)
        self.pushButton_20.setObjectName(u"pushButton_20")
        sizePolicy2.setHeightForWidth(self.pushButton_20.sizePolicy().hasHeightForWidth())
        self.pushButton_20.setSizePolicy(sizePolicy2)
        self.pushButton_20.setIconSize(QSize(16, 16))
        self.pushButton_20.setCheckable(False)
        self.pushButton_20.setAutoExclusive(True)
        self.pushButton_20.setAutoRepeatInterval(93)

        self.gridLayout.addWidget(self.pushButton_20, 0, 1, 1, 1)


        self.verticalLayout_7.addLayout(self.gridLayout)

        self.verticalLayout_7.setStretch(0, 1)
        self.verticalLayout_7.setStretch(1, 4)
        self.stackedWidget.addWidget(self.gesturesPage)
        self.controlsPage = QWidget()
        self.controlsPage.setObjectName(u"controlsPage")
        self.verticalLayout_controlsPage = QVBoxLayout(self.controlsPage)
        self.verticalLayout_controlsPage.setObjectName(u"verticalLayout_controlsPage")
        self.horizontalLayout_controlsHeader = QHBoxLayout()
        self.horizontalLayout_controlsHeader.setObjectName(u"horizontalLayout_controlsHeader")
        self.controlsCancelButton = QPushButton(self.controlsPage)
        self.controlsCancelButton.setObjectName(u"controlsCancelButton")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.controlsCancelButton.sizePolicy().hasHeightForWidth())
        self.controlsCancelButton.setSizePolicy(sizePolicy3)

        self.horizontalLayout_controlsHeader.addWidget(self.controlsCancelButton)

        self.controlsSaveButon = QPushButton(self.controlsPage)
        self.controlsSaveButon.setObjectName(u"controlsSaveButon")
        sizePolicy3.setHeightForWidth(self.controlsSaveButon.sizePolicy().hasHeightForWidth())
        self.controlsSaveButon.setSizePolicy(sizePolicy3)

        self.horizontalLayout_controlsHeader.addWidget(self.controlsSaveButon)

        self.controlsCleanButton = QPushButton(self.controlsPage)
        self.controlsCleanButton.setObjectName(u"controlsCleanButton")
        sizePolicy.setHeightForWidth(self.controlsCleanButton.sizePolicy().hasHeightForWidth())
        self.controlsCleanButton.setSizePolicy(sizePolicy)

        self.horizontalLayout_controlsHeader.addWidget(self.controlsCleanButton)

        self.gestureLabel = QLabel(self.controlsPage)
        self.gestureLabel.setObjectName(u"gestureLabel")
        self.gestureLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_controlsHeader.addWidget(self.gestureLabel)

        self.horizontalLayout_controlsHeader.setStretch(0, 1)
        self.horizontalLayout_controlsHeader.setStretch(1, 1)
        self.horizontalLayout_controlsHeader.setStretch(2, 1)
        self.horizontalLayout_controlsHeader.setStretch(3, 2)

        self.verticalLayout_controlsPage.addLayout(self.horizontalLayout_controlsHeader)

        self.stackedWidgetAcciones = QStackedWidget(self.controlsPage)
        self.stackedWidgetAcciones.setObjectName(u"stackedWidgetAcciones")
        self.page_category = QWidget()
        self.page_category.setObjectName(u"page_category")
        self.horizontalLayout_cat = QHBoxLayout(self.page_category)
        self.horizontalLayout_cat.setObjectName(u"horizontalLayout_cat")
        self.btn_cat_mando = QPushButton(self.page_category)
        self.btn_cat_mando.setObjectName(u"btn_cat_mando")
        sizePolicy.setHeightForWidth(self.btn_cat_mando.sizePolicy().hasHeightForWidth())
        self.btn_cat_mando.setSizePolicy(sizePolicy)

        self.horizontalLayout_cat.addWidget(self.btn_cat_mando)

        self.btn_cat_sys = QPushButton(self.page_category)
        self.btn_cat_sys.setObjectName(u"btn_cat_sys")
        sizePolicy.setHeightForWidth(self.btn_cat_sys.sizePolicy().hasHeightForWidth())
        self.btn_cat_sys.setSizePolicy(sizePolicy)

        self.horizontalLayout_cat.addWidget(self.btn_cat_sys)

        self.stackedWidgetAcciones.addWidget(self.page_category)
        self.page_mando = QWidget()
        self.page_mando.setObjectName(u"page_mando")
        self.verticalLayout_mando = QVBoxLayout(self.page_mando)
        self.verticalLayout_mando.setObjectName(u"verticalLayout_mando")
        self.btn_volver_cat1 = QPushButton(self.page_mando)
        self.btn_volver_cat1.setObjectName(u"btn_volver_cat1")
        sizePolicy3.setHeightForWidth(self.btn_volver_cat1.sizePolicy().hasHeightForWidth())
        self.btn_volver_cat1.setSizePolicy(sizePolicy3)

        self.verticalLayout_mando.addWidget(self.btn_volver_cat1)

        self.gridLayout_mando = QGridLayout()
        self.gridLayout_mando.setObjectName(u"gridLayout_mando")
        self.Start_button = QPushButton(self.page_mando)
        self.controlButtons = QButtonGroup(MainWindow)
        self.controlButtons.setObjectName(u"controlButtons")
        self.controlButtons.addButton(self.Start_button)
        self.Start_button.setObjectName(u"Start_button")
        sizePolicy.setHeightForWidth(self.Start_button.sizePolicy().hasHeightForWidth())
        self.Start_button.setSizePolicy(sizePolicy)
        self.Start_button.setCheckable(True)
        self.Start_button.setAutoExclusive(True)

        self.gridLayout_mando.addWidget(self.Start_button, 1, 1, 1, 1)

        self.Select_button = QPushButton(self.page_mando)
        self.controlButtons.addButton(self.Select_button)
        self.Select_button.setObjectName(u"Select_button")
        sizePolicy.setHeightForWidth(self.Select_button.sizePolicy().hasHeightForWidth())
        self.Select_button.setSizePolicy(sizePolicy)
        self.Select_button.setCheckable(True)
        self.Select_button.setAutoExclusive(True)

        self.gridLayout_mando.addWidget(self.Select_button, 1, 0, 1, 1)

        self.A_button = QPushButton(self.page_mando)
        self.controlButtons.addButton(self.A_button)
        self.A_button.setObjectName(u"A_button")
        sizePolicy.setHeightForWidth(self.A_button.sizePolicy().hasHeightForWidth())
        self.A_button.setSizePolicy(sizePolicy)
        self.A_button.setCheckable(True)
        self.A_button.setAutoExclusive(True)

        self.gridLayout_mando.addWidget(self.A_button, 0, 0, 1, 1)

        self.B_button = QPushButton(self.page_mando)
        self.controlButtons.addButton(self.B_button)
        self.B_button.setObjectName(u"B_button")
        sizePolicy.setHeightForWidth(self.B_button.sizePolicy().hasHeightForWidth())
        self.B_button.setSizePolicy(sizePolicy)
        self.B_button.setCheckable(True)
        self.B_button.setAutoExclusive(True)

        self.gridLayout_mando.addWidget(self.B_button, 0, 1, 1, 1)


        self.verticalLayout_mando.addLayout(self.gridLayout_mando)

        self.verticalLayout_mando.setStretch(0, 1)
        self.verticalLayout_mando.setStretch(1, 4)
        self.stackedWidgetAcciones.addWidget(self.page_mando)
        self.page_sys = QWidget()
        self.page_sys.setObjectName(u"page_sys")
        self.verticalLayout_sys = QVBoxLayout(self.page_sys)
        self.verticalLayout_sys.setObjectName(u"verticalLayout_sys")
        self.btn_volver_cat2 = QPushButton(self.page_sys)
        self.btn_volver_cat2.setObjectName(u"btn_volver_cat2")
        sizePolicy3.setHeightForWidth(self.btn_volver_cat2.sizePolicy().hasHeightForWidth())
        self.btn_volver_cat2.setSizePolicy(sizePolicy3)

        self.verticalLayout_sys.addWidget(self.btn_volver_cat2)

        self.gridLayout_sys = QGridLayout()
        self.gridLayout_sys.setObjectName(u"gridLayout_sys")
        self.btn_sys_modo = QPushButton(self.page_sys)
        self.controlButtons.addButton(self.btn_sys_modo)
        self.btn_sys_modo.setObjectName(u"btn_sys_modo")
        sizePolicy.setHeightForWidth(self.btn_sys_modo.sizePolicy().hasHeightForWidth())
        self.btn_sys_modo.setSizePolicy(sizePolicy)
        self.btn_sys_modo.setToolTipDuration(-4)
        self.btn_sys_modo.setLocale(QLocale(QLocale.Esperanto, QLocale.World))
        self.btn_sys_modo.setCheckable(True)
        self.btn_sys_modo.setAutoExclusive(True)

        self.gridLayout_sys.addWidget(self.btn_sys_modo, 0, 0, 1, 1)

        self.btn_sys_enter = QPushButton(self.page_sys)
        self.controlButtons.addButton(self.btn_sys_enter)
        self.btn_sys_enter.setObjectName(u"btn_sys_enter")
        sizePolicy.setHeightForWidth(self.btn_sys_enter.sizePolicy().hasHeightForWidth())
        self.btn_sys_enter.setSizePolicy(sizePolicy)
        self.btn_sys_enter.setCheckable(True)
        self.btn_sys_enter.setAutoExclusive(True)

        self.gridLayout_sys.addWidget(self.btn_sys_enter, 0, 1, 1, 1)


        self.verticalLayout_sys.addLayout(self.gridLayout_sys)

        self.verticalLayout_sys.setStretch(0, 1)
        self.verticalLayout_sys.setStretch(1, 3)
        self.stackedWidgetAcciones.addWidget(self.page_sys)

        self.verticalLayout_controlsPage.addWidget(self.stackedWidgetAcciones)

        self.label_calibracion = QLabel(self.controlsPage)
        self.label_calibracion.setObjectName(u"label_calibracion")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.label_calibracion.sizePolicy().hasHeightForWidth())
        self.label_calibracion.setSizePolicy(sizePolicy4)

        self.verticalLayout_controlsPage.addWidget(self.label_calibracion)

        self.horizontalLayout_calib = QHBoxLayout()
        self.horizontalLayout_calib.setObjectName(u"horizontalLayout_calib")
        self.btn_minus = QPushButton(self.controlsPage)
        self.btn_minus.setObjectName(u"btn_minus")
        sizePolicy.setHeightForWidth(self.btn_minus.sizePolicy().hasHeightForWidth())
        self.btn_minus.setSizePolicy(sizePolicy)

        self.horizontalLayout_calib.addWidget(self.btn_minus)

        self.verticalLayout_calib_center = QVBoxLayout()
        self.verticalLayout_calib_center.setObjectName(u"verticalLayout_calib_center")
        self.info_calib = QLabel(self.controlsPage)
        self.info_calib.setObjectName(u"info_calib")
        sizePolicy4.setHeightForWidth(self.info_calib.sizePolicy().hasHeightForWidth())
        self.info_calib.setSizePolicy(sizePolicy4)
        self.info_calib.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_calib_center.addWidget(self.info_calib)

        self.scoreContainerWidget = QWidget(self.controlsPage)
        self.scoreContainerWidget.setObjectName(u"scoreContainerWidget")
        sizePolicy.setHeightForWidth(self.scoreContainerWidget.sizePolicy().hasHeightForWidth())
        self.scoreContainerWidget.setSizePolicy(sizePolicy)
        self.gridLayout_scoreContainer = QGridLayout(self.scoreContainerWidget)
        self.gridLayout_scoreContainer.setObjectName(u"gridLayout_scoreContainer")
        self.gridLayout_scoreContainer.setContentsMargins(0, 0, 0, 0)
        self.scoreBar = QProgressBar(self.scoreContainerWidget)
        self.scoreBar.setObjectName(u"scoreBar")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.scoreBar.sizePolicy().hasHeightForWidth())
        self.scoreBar.setSizePolicy(sizePolicy5)
        self.scoreBar.setMinimumSize(QSize(0, 50))
        self.scoreBar.setMaximum(100)
        self.scoreBar.setValue(50)
        self.scoreBar.setTextVisible(False)

        self.gridLayout_scoreContainer.addWidget(self.scoreBar, 0, 0, 1, 1)

        self.scoreSlider = QSlider(self.scoreContainerWidget)
        self.scoreSlider.setObjectName(u"scoreSlider")
        sizePolicy5.setHeightForWidth(self.scoreSlider.sizePolicy().hasHeightForWidth())
        self.scoreSlider.setSizePolicy(sizePolicy5)
        self.scoreSlider.setMinimumSize(QSize(0, 50))
        self.scoreSlider.setMaximum(100)
        self.scoreSlider.setValue(50)
        self.scoreSlider.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_scoreContainer.addWidget(self.scoreSlider, 0, 0, 1, 1)


        self.verticalLayout_calib_center.addWidget(self.scoreContainerWidget)

        self.verticalLayout_calib_center.setStretch(0, 1)
        self.verticalLayout_calib_center.setStretch(1, 10)

        self.horizontalLayout_calib.addLayout(self.verticalLayout_calib_center)

        self.btn_plus = QPushButton(self.controlsPage)
        self.btn_plus.setObjectName(u"btn_plus")
        sizePolicy.setHeightForWidth(self.btn_plus.sizePolicy().hasHeightForWidth())
        self.btn_plus.setSizePolicy(sizePolicy)

        self.horizontalLayout_calib.addWidget(self.btn_plus)


        self.verticalLayout_controlsPage.addLayout(self.horizontalLayout_calib)

        self.verticalLayout_controlsPage.setStretch(0, 2)
        self.verticalLayout_controlsPage.setStretch(1, 6)
        self.verticalLayout_controlsPage.setStretch(3, 3)
        self.stackedWidget.addWidget(self.controlsPage)
        self.loadPage = QWidget()
        self.loadPage.setObjectName(u"loadPage")
        self.verticalLayout_load = QVBoxLayout(self.loadPage)
        self.verticalLayout_load.setObjectName(u"verticalLayout_load")
        self.label_load_title = QLabel(self.loadPage)
        self.label_load_title.setObjectName(u"label_load_title")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.label_load_title.sizePolicy().hasHeightForWidth())
        self.label_load_title.setSizePolicy(sizePolicy6)
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        self.label_load_title.setFont(font)
        self.label_load_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_load.addWidget(self.label_load_title)

        self.scrollAreaProfiles = QScrollArea(self.loadPage)
        self.scrollAreaProfiles.setObjectName(u"scrollAreaProfiles")
        self.scrollAreaProfiles.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.scrollAreaProfiles.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 783, 364))
        self.layoutProfiles = QGridLayout(self.scrollAreaWidgetContents)
        self.layoutProfiles.setObjectName(u"layoutProfiles")
        self.scrollAreaProfiles.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_load.addWidget(self.scrollAreaProfiles)

        self.horizontalLayout_load_buttons = QHBoxLayout()
        self.horizontalLayout_load_buttons.setObjectName(u"horizontalLayout_load_buttons")
        self.loadBackButton = QPushButton(self.loadPage)
        self.loadBackButton.setObjectName(u"loadBackButton")
        sizePolicy3.setHeightForWidth(self.loadBackButton.sizePolicy().hasHeightForWidth())
        self.loadBackButton.setSizePolicy(sizePolicy3)
        self.loadBackButton.setMinimumSize(QSize(0, 80))

        self.horizontalLayout_load_buttons.addWidget(self.loadBackButton)

        self.loadAcceptButton = QPushButton(self.loadPage)
        self.loadAcceptButton.setObjectName(u"loadAcceptButton")
        sizePolicy3.setHeightForWidth(self.loadAcceptButton.sizePolicy().hasHeightForWidth())
        self.loadAcceptButton.setSizePolicy(sizePolicy3)
        self.loadAcceptButton.setMinimumSize(QSize(0, 80))

        self.horizontalLayout_load_buttons.addWidget(self.loadAcceptButton)


        self.verticalLayout_load.addLayout(self.horizontalLayout_load_buttons)

        self.stackedWidget.addWidget(self.loadPage)
        self.keyboardPage = QWidget()
        self.keyboardPage.setObjectName(u"keyboardPage")
        self.verticalLayout_kb = QVBoxLayout(self.keyboardPage)
        self.verticalLayout_kb.setObjectName(u"verticalLayout_kb")
        self.keyboardDisplay = QLabel(self.keyboardPage)
        self.keyboardDisplay.setObjectName(u"keyboardDisplay")
        font1 = QFont()
        font1.setPointSize(24)
        font1.setBold(True)
        self.keyboardDisplay.setFont(font1)
        self.keyboardDisplay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_kb.addWidget(self.keyboardDisplay)

        self.keyboardContainerWidget = QWidget(self.keyboardPage)
        self.keyboardContainerWidget.setObjectName(u"keyboardContainerWidget")
        self.keyboardGridLayout = QGridLayout(self.keyboardContainerWidget)
        self.keyboardGridLayout.setObjectName(u"keyboardGridLayout")

        self.verticalLayout_kb.addWidget(self.keyboardContainerWidget)

        self.horizontalLayout_kb_buttons = QHBoxLayout()
        self.horizontalLayout_kb_buttons.setObjectName(u"horizontalLayout_kb_buttons")
        self.keyboardCancelButton = QPushButton(self.keyboardPage)
        self.keyboardCancelButton.setObjectName(u"keyboardCancelButton")
        sizePolicy.setHeightForWidth(self.keyboardCancelButton.sizePolicy().hasHeightForWidth())
        self.keyboardCancelButton.setSizePolicy(sizePolicy)

        self.horizontalLayout_kb_buttons.addWidget(self.keyboardCancelButton)

        self.keyboardBackspaceButton = QPushButton(self.keyboardPage)
        self.keyboardBackspaceButton.setObjectName(u"keyboardBackspaceButton")
        sizePolicy.setHeightForWidth(self.keyboardBackspaceButton.sizePolicy().hasHeightForWidth())
        self.keyboardBackspaceButton.setSizePolicy(sizePolicy)

        self.horizontalLayout_kb_buttons.addWidget(self.keyboardBackspaceButton)

        self.keyboardAcceptButton = QPushButton(self.keyboardPage)
        self.keyboardAcceptButton.setObjectName(u"keyboardAcceptButton")
        sizePolicy.setHeightForWidth(self.keyboardAcceptButton.sizePolicy().hasHeightForWidth())
        self.keyboardAcceptButton.setSizePolicy(sizePolicy)

        self.horizontalLayout_kb_buttons.addWidget(self.keyboardAcceptButton)


        self.verticalLayout_kb.addLayout(self.horizontalLayout_kb_buttons)

        self.verticalLayout_kb.setStretch(0, 1)
        self.verticalLayout_kb.setStretch(1, 5)
        self.verticalLayout_kb.setStretch(2, 1)
        self.stackedWidget.addWidget(self.keyboardPage)
        self.gamesPage = QWidget()
        self.gamesPage.setObjectName(u"gamesPage")
        self.verticalLayout_games = QVBoxLayout(self.gamesPage)
        self.verticalLayout_games.setObjectName(u"verticalLayout_games")
        self.label_games_title = QLabel(self.gamesPage)
        self.label_games_title.setObjectName(u"label_games_title")
        sizePolicy6.setHeightForWidth(self.label_games_title.sizePolicy().hasHeightForWidth())
        self.label_games_title.setSizePolicy(sizePolicy6)
        self.label_games_title.setFont(font)
        self.label_games_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_games.addWidget(self.label_games_title)

        self.scrollAreaGames = QScrollArea(self.gamesPage)
        self.scrollAreaGames.setObjectName(u"scrollAreaGames")
        self.scrollAreaGames.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.scrollAreaGames.setWidgetResizable(True)
        self.scrollAreaGamesContents = QWidget()
        self.scrollAreaGamesContents.setObjectName(u"scrollAreaGamesContents")
        self.scrollAreaGamesContents.setGeometry(QRect(0, 0, 783, 364))
        self.layoutGames = QGridLayout(self.scrollAreaGamesContents)
        self.layoutGames.setObjectName(u"layoutGames")
        self.scrollAreaGames.setWidget(self.scrollAreaGamesContents)

        self.verticalLayout_games.addWidget(self.scrollAreaGames)

        self.horizontalLayout_games_buttons = QHBoxLayout()
        self.horizontalLayout_games_buttons.setObjectName(u"horizontalLayout_games_buttons")
        self.gamesBackButton = QPushButton(self.gamesPage)
        self.gamesBackButton.setObjectName(u"gamesBackButton")
        sizePolicy3.setHeightForWidth(self.gamesBackButton.sizePolicy().hasHeightForWidth())
        self.gamesBackButton.setSizePolicy(sizePolicy3)
        self.gamesBackButton.setMinimumSize(QSize(0, 80))

        self.horizontalLayout_games_buttons.addWidget(self.gamesBackButton)

        self.gamesScanButton = QPushButton(self.gamesPage)
        self.gamesScanButton.setObjectName(u"gamesScanButton")
        sizePolicy3.setHeightForWidth(self.gamesScanButton.sizePolicy().hasHeightForWidth())
        self.gamesScanButton.setSizePolicy(sizePolicy3)
        self.gamesScanButton.setMinimumSize(QSize(0, 80))

        self.horizontalLayout_games_buttons.addWidget(self.gamesScanButton)

        self.scanFolderButton = QPushButton(self.gamesPage)
        self.scanFolderButton.setObjectName(u"scanFolderButton")
        sizePolicy3.setHeightForWidth(self.scanFolderButton.sizePolicy().hasHeightForWidth())
        self.scanFolderButton.setSizePolicy(sizePolicy3)
        self.scanFolderButton.setMinimumSize(QSize(0, 80))

        self.horizontalLayout_games_buttons.addWidget(self.scanFolderButton)


        self.verticalLayout_games.addLayout(self.horizontalLayout_games_buttons)

        self.stackedWidget.addWidget(self.gamesPage)
        self.explorerPage = QWidget()
        self.explorerPage.setObjectName(u"explorerPage")
        self.verticalLayout_explorer = QVBoxLayout(self.explorerPage)
        self.verticalLayout_explorer.setObjectName(u"verticalLayout_explorer")
        self.label_explorer_path = QLabel(self.explorerPage)
        self.label_explorer_path.setObjectName(u"label_explorer_path")
        font2 = QFont()
        font2.setPointSize(14)
        font2.setBold(True)
        self.label_explorer_path.setFont(font2)
        self.label_explorer_path.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_explorer.addWidget(self.label_explorer_path)

        self.scrollAreaExplorer = QScrollArea(self.explorerPage)
        self.scrollAreaExplorer.setObjectName(u"scrollAreaExplorer")
        self.scrollAreaExplorer.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.scrollAreaExplorer.setWidgetResizable(True)
        self.scrollAreaExplorerContents = QWidget()
        self.scrollAreaExplorerContents.setObjectName(u"scrollAreaExplorerContents")
        self.scrollAreaExplorerContents.setGeometry(QRect(0, 0, 783, 374))
        self.layoutExplorer = QGridLayout(self.scrollAreaExplorerContents)
        self.layoutExplorer.setObjectName(u"layoutExplorer")
        self.scrollAreaExplorer.setWidget(self.scrollAreaExplorerContents)

        self.verticalLayout_explorer.addWidget(self.scrollAreaExplorer)

        self.explorer_buttons_layout = QHBoxLayout()
        self.explorer_buttons_layout.setObjectName(u"explorer_buttons_layout")
        self.explorerCancelButton = QPushButton(self.explorerPage)
        self.explorerCancelButton.setObjectName(u"explorerCancelButton")
        self.explorerCancelButton.setMinimumSize(QSize(0, 80))

        self.explorer_buttons_layout.addWidget(self.explorerCancelButton)

        self.explorerUpButton = QPushButton(self.explorerPage)
        self.explorerUpButton.setObjectName(u"explorerUpButton")
        self.explorerUpButton.setMinimumSize(QSize(0, 80))

        self.explorer_buttons_layout.addWidget(self.explorerUpButton)

        self.explorerSelectButton = QPushButton(self.explorerPage)
        self.explorerSelectButton.setObjectName(u"explorerSelectButton")
        self.explorerSelectButton.setMinimumSize(QSize(0, 80))

        self.explorer_buttons_layout.addWidget(self.explorerSelectButton)


        self.verticalLayout_explorer.addLayout(self.explorer_buttons_layout)

        self.stackedWidget.addWidget(self.explorerPage)

        self.verticalLayout_6.addWidget(self.stackedWidget)


        self.verticalLayout.addLayout(self.verticalLayout_6)

        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 4)

        self.horizontalLayout.addLayout(self.verticalLayout)

        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 4)

        self.horizontalLayout_2.addLayout(self.horizontalLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1032, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(0)
        self.stackedWidgetAcciones.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.videoLabel.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.pipButton.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.stopButton.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.pushButton_4.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.changeControlsButton.setText(QCoreApplication.translate("MainWindow", u"Cambiar controles", None))
        self.gamesButton.setText(QCoreApplication.translate("MainWindow", u"\U0001f3ae MIS JUEGOS", None))
        self.pushButton_5.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.gesturesBackButton.setText(QCoreApplication.translate("MainWindow", u"\u25c0 Volver  sin guardar", None))
        self.gesturesBackButton.setProperty(u"type", "")
        self.gesturesSaveLocalButton.setText(QCoreApplication.translate("MainWindow", u"Guardar y volver", None))
        self.gesturesSaveLocalButton.setProperty(u"type", QCoreApplication.translate("MainWindow", u"primary", None))
        self.gesturesLoadButton.setText(QCoreApplication.translate("MainWindow", u"Cargar archivo", None))
        self.gesturesSaveExternalButton.setText(QCoreApplication.translate("MainWindow", u"Guardar archivo", None))
        self.pushButton_22.setText(QCoreApplication.translate("MainWindow", u"Abrir boca", None))
        self.pushButton_22.setProperty(u"gesture", QCoreApplication.translate("MainWindow", u"jawOpen", None))
        self.pushButton_18.setText(QCoreApplication.translate("MainWindow", u"Gui\u00f1o", None))
        self.pushButton_18.setProperty(u"gesture", QCoreApplication.translate("MainWindow", u"eyeBlinkRight", None))
        self.pushButton_19.setText(QCoreApplication.translate("MainWindow", u"Cejas", None))
        self.pushButton_19.setProperty(u"gesture", QCoreApplication.translate("MainWindow", u"eyeBrowsUp", None))
        self.pushButton_21.setText(QCoreApplication.translate("MainWindow", u"Morritos", None))
        self.pushButton_21.setProperty(u"gesture", QCoreApplication.translate("MainWindow", u"mouthPucker", None))
        self.pushButton_20.setText(QCoreApplication.translate("MainWindow", u"Sonrisa", None))
        self.pushButton_20.setProperty(u"gesture", QCoreApplication.translate("MainWindow", u"smile", None))
        self.controlsCancelButton.setText(QCoreApplication.translate("MainWindow", u"\u25c0 VOLVER", None))
        self.controlsSaveButon.setText(QCoreApplication.translate("MainWindow", u"\u2714 GUARDAR Y VOLVER", None))
        self.controlsSaveButon.setProperty(u"type", QCoreApplication.translate("MainWindow", u"primary", None))
        self.controlsCleanButton.setText(QCoreApplication.translate("MainWindow", u"Vaciar", None))
        self.gestureLabel.setText(QCoreApplication.translate("MainWindow", u"Gesto", None))
        self.btn_cat_mando.setText(QCoreApplication.translate("MainWindow", u"\U0001f3ae BOT\U000000d3N DEL MANDO", None))
        self.btn_cat_sys.setText(QCoreApplication.translate("MainWindow", u"\u2699\ufe0f ACCI\u00d3N DE SISTEMA", None))
        self.btn_volver_cat1.setText(QCoreApplication.translate("MainWindow", u"\u25c0  CAMBIAR TIPO DE ACCI\u00d3N", None))
        self.btn_volver_cat1.setProperty(u"type", QCoreApplication.translate("MainWindow", u"secondary", None))
        self.Start_button.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.Start_button.setProperty(u"gamepadInput", QCoreApplication.translate("MainWindow", u"XUSB_GAMEPAD_START", None))
        self.Select_button.setText(QCoreApplication.translate("MainWindow", u"Select", None))
        self.Select_button.setProperty(u"gamepadInput", QCoreApplication.translate("MainWindow", u"XUSB_GAMEPAD_BACK", None))
        self.A_button.setText(QCoreApplication.translate("MainWindow", u"A", None))
        self.A_button.setProperty(u"gamepadInput", QCoreApplication.translate("MainWindow", u"XUSB_GAMEPAD_A", None))
        self.B_button.setText(QCoreApplication.translate("MainWindow", u"B", None))
        self.B_button.setProperty(u"gamepadInput", QCoreApplication.translate("MainWindow", u"XUSB_GAMEPAD_B", None))
        self.btn_volver_cat2.setText(QCoreApplication.translate("MainWindow", u"\u25c0  CAMBIAR TIPO DE ACCI\u00d3N", None))
        self.btn_volver_cat2.setProperty(u"type", QCoreApplication.translate("MainWindow", u"secondary", None))
        self.btn_sys_modo.setText(QCoreApplication.translate("MainWindow", u"Cambiar Modo Movimiento", None))
        self.btn_sys_modo.setProperty(u"gamepadInput", QCoreApplication.translate("MainWindow", u"SYS_CHANGE_MODE", None))
        self.btn_sys_enter.setText(QCoreApplication.translate("MainWindow", u"Click", None))
        self.btn_sys_enter.setProperty(u"gamepadInput", QCoreApplication.translate("MainWindow", u"SYS_NAV_ENTER", None))
        self.label_calibracion.setText(QCoreApplication.translate("MainWindow", u"Calibra la sensibilidad:", None))
        self.btn_minus.setText(QCoreApplication.translate("MainWindow", u"\u2796", None))
        self.info_calib.setText(QCoreApplication.translate("MainWindow", u"Umbral actual: 50%", None))
        self.btn_plus.setText(QCoreApplication.translate("MainWindow", u"\u2795", None))
        self.label_load_title.setText(QCoreApplication.translate("MainWindow", u"SELECCIONAR PERFIL", None))
        self.scrollAreaProfiles.setStyleSheet(QCoreApplication.translate("MainWindow", u"QScrollArea { border: none; background: transparent; } QWidget#scrollAreaWidgetContents { background: transparent; }", None))
        self.loadBackButton.setText(QCoreApplication.translate("MainWindow", u"\u25c0 VOLVER", None))
        self.loadBackButton.setProperty(u"type", QCoreApplication.translate("MainWindow", u"secondary", None))
        self.loadAcceptButton.setText(QCoreApplication.translate("MainWindow", u"\u2714 ACEPTAR", None))
        self.loadAcceptButton.setProperty(u"type", QCoreApplication.translate("MainWindow", u"primary", None))
        self.keyboardDisplay.setStyleSheet(QCoreApplication.translate("MainWindow", u"background-color: #1e1e1e; border: 2px solid #555555; border-radius: 10px; padding: 10px; color: #FFEB3B;", None))
        self.keyboardDisplay.setText("")
        self.keyboardCancelButton.setText(QCoreApplication.translate("MainWindow", u"\u25c0 CANCELAR", None))
        self.keyboardCancelButton.setProperty(u"type", QCoreApplication.translate("MainWindow", u"secondary", None))
        self.keyboardBackspaceButton.setText(QCoreApplication.translate("MainWindow", u"\u232b BORRAR", None))
        self.keyboardAcceptButton.setText(QCoreApplication.translate("MainWindow", u"\u2714 GUARDAR", None))
        self.keyboardAcceptButton.setProperty(u"type", QCoreApplication.translate("MainWindow", u"primary", None))
        self.label_games_title.setText(QCoreApplication.translate("MainWindow", u"CAT\u00c1LOGO DE JUEGOS", None))
        self.scrollAreaGames.setStyleSheet(QCoreApplication.translate("MainWindow", u"QScrollArea { border: none; background: transparent; } QWidget#scrollAreaGamesContents { background: transparent; }", None))
        self.gamesBackButton.setText(QCoreApplication.translate("MainWindow", u"\u25c0 VOLVER AL MEN\u00da", None))
        self.gamesScanButton.setText(QCoreApplication.translate("MainWindow", u"\U0001f50d ESCANEAR STEAM", None))
        self.scanFolderButton.setText(QCoreApplication.translate("MainWindow", u"\U0001f4c1 ESCANEAR CARPETA", None))
        self.label_explorer_path.setText(QCoreApplication.translate("MainWindow", u"Ruta actual: C:\\", None))
        self.scrollAreaExplorer.setStyleSheet(QCoreApplication.translate("MainWindow", u"QScrollArea { border: none; background: transparent; } QWidget#scrollAreaExplorerContents { background: transparent; }", None))
        self.explorerCancelButton.setText(QCoreApplication.translate("MainWindow", u"\u274c CANCELAR", None))
        self.explorerUpButton.setText(QCoreApplication.translate("MainWindow", u"\u2b06 SUBIR NIVEL", None))
        self.explorerSelectButton.setText(QCoreApplication.translate("MainWindow", u"\u2705 ELEGIR ESTA CARPETA", None))
    # retranslateUi


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

from custom_widgets import QRangeSlider

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
        self.verticalLayout_8 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
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

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.controllerImage = QLabel(self.centralwidget)
        self.controllerImage.setObjectName(u"controllerImage")
        self.controllerImage.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.controllerImage.sizePolicy().hasHeightForWidth())
        self.controllerImage.setSizePolicy(sizePolicy1)
        self.controllerImage.setPixmap(QPixmap(u"images/controlGB.png"))
        self.controllerImage.setScaledContents(True)
        self.controllerImage.setAlignment(Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignTop)

        self.verticalLayout_4.addWidget(self.controllerImage)


        self.verticalLayout_3.addLayout(self.verticalLayout_4)

        self.verticalLayout_3.setStretch(0, 2)
        self.verticalLayout_3.setStretch(1, 1)
        self.verticalLayout_3.setStretch(2, 5)

        self.verticalLayout_2.addLayout(self.verticalLayout_3)

        self.verticalLayout_2.setStretch(0, 3)

        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.pipButton = QPushButton(self.centralwidget)
        self.pipButton.setObjectName(u"pipButton")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.pipButton.sizePolicy().hasHeightForWidth())
        self.pipButton.setSizePolicy(sizePolicy2)

        self.horizontalLayout_3.addWidget(self.pipButton)

        self.stopButton = QPushButton(self.centralwidget)
        self.stopButton.setObjectName(u"stopButton")
        sizePolicy2.setHeightForWidth(self.stopButton.sizePolicy().hasHeightForWidth())
        self.stopButton.setSizePolicy(sizePolicy2)
        self.stopButton.setIconSize(QSize(27, 16))

        self.horizontalLayout_3.addWidget(self.stopButton)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        sizePolicy.setHeightForWidth(self.stackedWidget.sizePolicy().hasHeightForWidth())
        self.stackedWidget.setSizePolicy(sizePolicy)
        self.platformsPage = QWidget()
        self.platformsPage.setObjectName(u"platformsPage")
        self.platformsPage.setSizeIncrement(QSize(5, 0))
        self.verticalLayout_games = QVBoxLayout(self.platformsPage)
        self.verticalLayout_games.setObjectName(u"verticalLayout_games")
        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_platforms_title = QLabel(self.platformsPage)
        self.label_platforms_title.setObjectName(u"label_platforms_title")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_platforms_title.sizePolicy().hasHeightForWidth())
        self.label_platforms_title.setSizePolicy(sizePolicy3)
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        self.label_platforms_title.setFont(font)
        self.label_platforms_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_8.addWidget(self.label_platforms_title)

        self.emulatorsButton = QPushButton(self.platformsPage)
        self.emulatorsButton.setObjectName(u"emulatorsButton")
        sizePolicy.setHeightForWidth(self.emulatorsButton.sizePolicy().hasHeightForWidth())
        self.emulatorsButton.setSizePolicy(sizePolicy)

        self.horizontalLayout_8.addWidget(self.emulatorsButton)

        self.controlsButton = QPushButton(self.platformsPage)
        self.controlsButton.setObjectName(u"controlsButton")
        sizePolicy.setHeightForWidth(self.controlsButton.sizePolicy().hasHeightForWidth())
        self.controlsButton.setSizePolicy(sizePolicy)

        self.horizontalLayout_8.addWidget(self.controlsButton)

        self.horizontalLayout_8.setStretch(0, 2)
        self.horizontalLayout_8.setStretch(1, 1)
        self.horizontalLayout_8.setStretch(2, 1)

        self.verticalLayout_games.addLayout(self.horizontalLayout_8)

        self.scrollAreaPlaforms = QScrollArea(self.platformsPage)
        self.scrollAreaPlaforms.setObjectName(u"scrollAreaPlaforms")
        self.scrollAreaPlaforms.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.scrollAreaPlaforms.setLocale(QLocale(QLocale.English, QLocale.Vanuatu))
        self.scrollAreaPlaforms.setWidgetResizable(True)
        self.scrollAreaPlatformsContents = QWidget()
        self.scrollAreaPlatformsContents.setObjectName(u"scrollAreaPlatformsContents")
        self.scrollAreaPlatformsContents.setGeometry(QRect(0, 0, 783, 374))
        self.layoutPlatforms = QGridLayout(self.scrollAreaPlatformsContents)
        self.layoutPlatforms.setObjectName(u"layoutPlatforms")
        self.scrollAreaPlaforms.setWidget(self.scrollAreaPlatformsContents)

        self.verticalLayout_games.addWidget(self.scrollAreaPlaforms)

        self.horizontalLayout_games_buttons = QHBoxLayout()
        self.horizontalLayout_games_buttons.setObjectName(u"horizontalLayout_games_buttons")
        self.gamesScanButton = QPushButton(self.platformsPage)
        self.gamesScanButton.setObjectName(u"gamesScanButton")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.gamesScanButton.sizePolicy().hasHeightForWidth())
        self.gamesScanButton.setSizePolicy(sizePolicy4)
        self.gamesScanButton.setMinimumSize(QSize(0, 80))

        self.horizontalLayout_games_buttons.addWidget(self.gamesScanButton)

        self.scanFolderButton = QPushButton(self.platformsPage)
        self.scanFolderButton.setObjectName(u"scanFolderButton")
        sizePolicy4.setHeightForWidth(self.scanFolderButton.sizePolicy().hasHeightForWidth())
        self.scanFolderButton.setSizePolicy(sizePolicy4)
        self.scanFolderButton.setMinimumSize(QSize(0, 80))

        self.horizontalLayout_games_buttons.addWidget(self.scanFolderButton)


        self.verticalLayout_games.addLayout(self.horizontalLayout_games_buttons)

        self.verticalLayout_games.setStretch(0, 1)
        self.verticalLayout_games.setStretch(1, 5)
        self.verticalLayout_games.setStretch(2, 1)
        self.stackedWidget.addWidget(self.platformsPage)
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

        self.gesturesSaveExternalButton = QPushButton(self.gesturesPage)
        self.gesturesSaveExternalButton.setObjectName(u"gesturesSaveExternalButton")
        sizePolicy2.setHeightForWidth(self.gesturesSaveExternalButton.sizePolicy().hasHeightForWidth())
        self.gesturesSaveExternalButton.setSizePolicy(sizePolicy2)

        self.horizontalLayout_5.addWidget(self.gesturesSaveExternalButton)

        self.gesturesLoadButton = QPushButton(self.gesturesPage)
        self.gesturesLoadButton.setObjectName(u"gesturesLoadButton")
        sizePolicy2.setHeightForWidth(self.gesturesLoadButton.sizePolicy().hasHeightForWidth())
        self.gesturesLoadButton.setSizePolicy(sizePolicy2)

        self.horizontalLayout_5.addWidget(self.gesturesLoadButton)

        self.horizontalLayout_5.setStretch(0, 1)
        self.horizontalLayout_5.setStretch(1, 1)
        self.horizontalLayout_5.setStretch(2, 1)
        self.horizontalLayout_5.setStretch(3, 1)

        self.verticalLayout_7.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.pushButton_21 = QPushButton(self.gesturesPage)
        self.gestureButtons = QButtonGroup(MainWindow)
        self.gestureButtons.setObjectName(u"gestureButtons")
        self.gestureButtons.addButton(self.pushButton_21)
        self.pushButton_21.setObjectName(u"pushButton_21")
        sizePolicy2.setHeightForWidth(self.pushButton_21.sizePolicy().hasHeightForWidth())
        self.pushButton_21.setSizePolicy(sizePolicy2)
        self.pushButton_21.setIconSize(QSize(16, 16))
        self.pushButton_21.setCheckable(False)
        self.pushButton_21.setAutoExclusive(True)

        self.gridLayout_2.addWidget(self.pushButton_21, 0, 2, 1, 1)

        self.pushButton_20 = QPushButton(self.gesturesPage)
        self.gestureButtons.addButton(self.pushButton_20)
        self.pushButton_20.setObjectName(u"pushButton_20")
        sizePolicy2.setHeightForWidth(self.pushButton_20.sizePolicy().hasHeightForWidth())
        self.pushButton_20.setSizePolicy(sizePolicy2)
        self.pushButton_20.setIconSize(QSize(16, 16))
        self.pushButton_20.setCheckable(False)
        self.pushButton_20.setAutoExclusive(True)
        self.pushButton_20.setAutoRepeatInterval(93)

        self.gridLayout_2.addWidget(self.pushButton_20, 0, 1, 1, 1)

        self.pushButton_18 = QPushButton(self.gesturesPage)
        self.gestureButtons.addButton(self.pushButton_18)
        self.pushButton_18.setObjectName(u"pushButton_18")
        sizePolicy2.setHeightForWidth(self.pushButton_18.sizePolicy().hasHeightForWidth())
        self.pushButton_18.setSizePolicy(sizePolicy2)
        self.pushButton_18.setIconSize(QSize(16, 16))
        self.pushButton_18.setCheckable(False)
        self.pushButton_18.setAutoExclusive(True)

        self.gridLayout_2.addWidget(self.pushButton_18, 0, 0, 1, 1)

        self.pushButton_19 = QPushButton(self.gesturesPage)
        self.gestureButtons.addButton(self.pushButton_19)
        self.pushButton_19.setObjectName(u"pushButton_19")
        sizePolicy2.setHeightForWidth(self.pushButton_19.sizePolicy().hasHeightForWidth())
        self.pushButton_19.setSizePolicy(sizePolicy2)
        self.pushButton_19.setIconSize(QSize(16, 16))
        self.pushButton_19.setCheckable(False)
        self.pushButton_19.setAutoExclusive(True)

        self.gridLayout_2.addWidget(self.pushButton_19, 1, 0, 1, 1)

        self.pushButton_22 = QPushButton(self.gesturesPage)
        self.gestureButtons.addButton(self.pushButton_22)
        self.pushButton_22.setObjectName(u"pushButton_22")
        sizePolicy2.setHeightForWidth(self.pushButton_22.sizePolicy().hasHeightForWidth())
        self.pushButton_22.setSizePolicy(sizePolicy2)
        self.pushButton_22.setCheckable(False)
        self.pushButton_22.setAutoExclusive(True)

        self.gridLayout_2.addWidget(self.pushButton_22, 1, 1, 1, 1)


        self.horizontalLayout_10.addLayout(self.gridLayout_2)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer_4)

        self.noseButton = QPushButton(self.gesturesPage)
        self.noseButton.setObjectName(u"noseButton")
        sizePolicy2.setHeightForWidth(self.noseButton.sizePolicy().hasHeightForWidth())
        self.noseButton.setSizePolicy(sizePolicy2)

        self.verticalLayout_5.addWidget(self.noseButton)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer_5)

        self.verticalLayout_5.setStretch(0, 2)
        self.verticalLayout_5.setStretch(1, 3)
        self.verticalLayout_5.setStretch(2, 2)

        self.horizontalLayout_10.addLayout(self.verticalLayout_5)

        self.horizontalLayout_10.setStretch(0, 3)
        self.horizontalLayout_10.setStretch(1, 1)

        self.verticalLayout_7.addLayout(self.horizontalLayout_10)

        self.verticalLayout_7.setStretch(0, 1)
        self.verticalLayout_7.setStretch(1, 5)
        self.stackedWidget.addWidget(self.gesturesPage)
        self.controlsPage = QWidget()
        self.controlsPage.setObjectName(u"controlsPage")
        self.verticalLayout_controlsPage = QVBoxLayout(self.controlsPage)
        self.verticalLayout_controlsPage.setObjectName(u"verticalLayout_controlsPage")
        self.horizontalLayout_controlsHeader = QHBoxLayout()
        self.horizontalLayout_controlsHeader.setObjectName(u"horizontalLayout_controlsHeader")
        self.controlsCancelButton = QPushButton(self.controlsPage)
        self.controlsCancelButton.setObjectName(u"controlsCancelButton")
        sizePolicy4.setHeightForWidth(self.controlsCancelButton.sizePolicy().hasHeightForWidth())
        self.controlsCancelButton.setSizePolicy(sizePolicy4)

        self.horizontalLayout_controlsHeader.addWidget(self.controlsCancelButton)

        self.controlsSaveButon = QPushButton(self.controlsPage)
        self.controlsSaveButon.setObjectName(u"controlsSaveButon")
        sizePolicy4.setHeightForWidth(self.controlsSaveButon.sizePolicy().hasHeightForWidth())
        self.controlsSaveButon.setSizePolicy(sizePolicy4)

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
        sizePolicy4.setHeightForWidth(self.btn_volver_cat1.sizePolicy().hasHeightForWidth())
        self.btn_volver_cat1.setSizePolicy(sizePolicy4)

        self.verticalLayout_mando.addWidget(self.btn_volver_cat1)

        self.gridLayout_mando = QGridLayout()
        self.gridLayout_mando.setObjectName(u"gridLayout_mando")
        self.Y_button = QPushButton(self.page_mando)
        self.controlButtons = QButtonGroup(MainWindow)
        self.controlButtons.setObjectName(u"controlButtons")
        self.controlButtons.addButton(self.Y_button)
        self.Y_button.setObjectName(u"Y_button")
        sizePolicy.setHeightForWidth(self.Y_button.sizePolicy().hasHeightForWidth())
        self.Y_button.setSizePolicy(sizePolicy)
        self.Y_button.setCheckable(True)
        self.Y_button.setAutoExclusive(True)

        self.gridLayout_mando.addWidget(self.Y_button, 0, 2, 1, 1)

        self.X_button = QPushButton(self.page_mando)
        self.controlButtons.addButton(self.X_button)
        self.X_button.setObjectName(u"X_button")
        sizePolicy.setHeightForWidth(self.X_button.sizePolicy().hasHeightForWidth())
        self.X_button.setSizePolicy(sizePolicy)
        self.X_button.setCheckable(True)
        self.X_button.setAutoExclusive(True)

        self.gridLayout_mando.addWidget(self.X_button, 0, 3, 1, 1)

        self.Select_button = QPushButton(self.page_mando)
        self.controlButtons.addButton(self.Select_button)
        self.Select_button.setObjectName(u"Select_button")
        sizePolicy.setHeightForWidth(self.Select_button.sizePolicy().hasHeightForWidth())
        self.Select_button.setSizePolicy(sizePolicy)
        self.Select_button.setCheckable(True)
        self.Select_button.setAutoExclusive(True)

        self.gridLayout_mando.addWidget(self.Select_button, 2, 0, 1, 1)

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

        self.Start_button = QPushButton(self.page_mando)
        self.controlButtons.addButton(self.Start_button)
        self.Start_button.setObjectName(u"Start_button")
        sizePolicy.setHeightForWidth(self.Start_button.sizePolicy().hasHeightForWidth())
        self.Start_button.setSizePolicy(sizePolicy)
        self.Start_button.setCheckable(True)
        self.Start_button.setAutoExclusive(True)

        self.gridLayout_mando.addWidget(self.Start_button, 2, 1, 1, 1)

        self.L2_button = QPushButton(self.page_mando)
        self.controlButtons.addButton(self.L2_button)
        self.L2_button.setObjectName(u"L2_button")
        sizePolicy.setHeightForWidth(self.L2_button.sizePolicy().hasHeightForWidth())
        self.L2_button.setSizePolicy(sizePolicy)
        self.L2_button.setCheckable(True)
        self.L2_button.setAutoExclusive(True)

        self.gridLayout_mando.addWidget(self.L2_button, 1, 1, 1, 1)

        self.R1_button = QPushButton(self.page_mando)
        self.controlButtons.addButton(self.R1_button)
        self.R1_button.setObjectName(u"R1_button")
        sizePolicy.setHeightForWidth(self.R1_button.sizePolicy().hasHeightForWidth())
        self.R1_button.setSizePolicy(sizePolicy)
        self.R1_button.setCheckable(True)
        self.R1_button.setAutoExclusive(True)

        self.gridLayout_mando.addWidget(self.R1_button, 1, 2, 1, 1)

        self.R2_button = QPushButton(self.page_mando)
        self.controlButtons.addButton(self.R2_button)
        self.R2_button.setObjectName(u"R2_button")
        sizePolicy.setHeightForWidth(self.R2_button.sizePolicy().hasHeightForWidth())
        self.R2_button.setSizePolicy(sizePolicy)
        self.R2_button.setCheckable(True)
        self.R2_button.setAutoExclusive(True)

        self.gridLayout_mando.addWidget(self.R2_button, 1, 3, 1, 1)

        self.L1_button = QPushButton(self.page_mando)
        self.controlButtons.addButton(self.L1_button)
        self.L1_button.setObjectName(u"L1_button")
        sizePolicy.setHeightForWidth(self.L1_button.sizePolicy().hasHeightForWidth())
        self.L1_button.setSizePolicy(sizePolicy)
        self.L1_button.setCheckable(True)
        self.L1_button.setAutoExclusive(True)

        self.gridLayout_mando.addWidget(self.L1_button, 1, 0, 1, 1)


        self.verticalLayout_mando.addLayout(self.gridLayout_mando)

        self.verticalLayout_mando.setStretch(0, 1)
        self.verticalLayout_mando.setStretch(1, 4)
        self.stackedWidgetAcciones.addWidget(self.page_mando)
        self.page_sys = QWidget()
        self.page_sys.setObjectName(u"page_sys")
        self.page_sys.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.verticalLayout_sys = QVBoxLayout(self.page_sys)
        self.verticalLayout_sys.setObjectName(u"verticalLayout_sys")
        self.btn_volver_cat2 = QPushButton(self.page_sys)
        self.btn_volver_cat2.setObjectName(u"btn_volver_cat2")
        sizePolicy4.setHeightForWidth(self.btn_volver_cat2.sizePolicy().hasHeightForWidth())
        self.btn_volver_cat2.setSizePolicy(sizePolicy4)

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

        self.btn_sys_restore = QPushButton(self.page_sys)
        self.controlButtons.addButton(self.btn_sys_restore)
        self.btn_sys_restore.setObjectName(u"btn_sys_restore")
        sizePolicy2.setHeightForWidth(self.btn_sys_restore.sizePolicy().hasHeightForWidth())
        self.btn_sys_restore.setSizePolicy(sizePolicy2)
        self.btn_sys_restore.setCheckable(True)
        self.btn_sys_restore.setAutoExclusive(True)

        self.gridLayout_sys.addWidget(self.btn_sys_restore, 1, 0, 1, 1)


        self.verticalLayout_sys.addLayout(self.gridLayout_sys)

        self.verticalLayout_sys.setStretch(0, 1)
        self.verticalLayout_sys.setStretch(1, 3)
        self.stackedWidgetAcciones.addWidget(self.page_sys)

        self.verticalLayout_controlsPage.addWidget(self.stackedWidgetAcciones)

        self.label_calibracion = QLabel(self.controlsPage)
        self.label_calibracion.setObjectName(u"label_calibracion")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.label_calibracion.sizePolicy().hasHeightForWidth())
        self.label_calibracion.setSizePolicy(sizePolicy5)

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
        sizePolicy5.setHeightForWidth(self.info_calib.sizePolicy().hasHeightForWidth())
        self.info_calib.setSizePolicy(sizePolicy5)
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
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.scoreBar.sizePolicy().hasHeightForWidth())
        self.scoreBar.setSizePolicy(sizePolicy6)
        self.scoreBar.setMinimumSize(QSize(0, 50))
        self.scoreBar.setMaximum(100)
        self.scoreBar.setValue(50)
        self.scoreBar.setTextVisible(False)

        self.gridLayout_scoreContainer.addWidget(self.scoreBar, 0, 0, 1, 1)

        self.scoreSlider = QSlider(self.scoreContainerWidget)
        self.scoreSlider.setObjectName(u"scoreSlider")
        sizePolicy6.setHeightForWidth(self.scoreSlider.sizePolicy().hasHeightForWidth())
        self.scoreSlider.setSizePolicy(sizePolicy6)
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
        sizePolicy3.setHeightForWidth(self.label_load_title.sizePolicy().hasHeightForWidth())
        self.label_load_title.setSizePolicy(sizePolicy3)
        self.label_load_title.setFont(font)
        self.label_load_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_load.addWidget(self.label_load_title)

        self.scrollAreaProfiles = QScrollArea(self.loadPage)
        self.scrollAreaProfiles.setObjectName(u"scrollAreaProfiles")
        self.scrollAreaProfiles.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.scrollAreaProfiles.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 783, 413))
        self.layoutProfiles = QGridLayout(self.scrollAreaWidgetContents)
        self.layoutProfiles.setObjectName(u"layoutProfiles")
        self.scrollAreaProfiles.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_load.addWidget(self.scrollAreaProfiles)

        self.horizontalLayout_load_buttons = QHBoxLayout()
        self.horizontalLayout_load_buttons.setObjectName(u"horizontalLayout_load_buttons")
        self.loadBackButton = QPushButton(self.loadPage)
        self.loadBackButton.setObjectName(u"loadBackButton")
        sizePolicy4.setHeightForWidth(self.loadBackButton.sizePolicy().hasHeightForWidth())
        self.loadBackButton.setSizePolicy(sizePolicy4)
        self.loadBackButton.setMinimumSize(QSize(0, 80))

        self.horizontalLayout_load_buttons.addWidget(self.loadBackButton)

        self.loadAcceptButton = QPushButton(self.loadPage)
        self.loadAcceptButton.setObjectName(u"loadAcceptButton")
        sizePolicy4.setHeightForWidth(self.loadAcceptButton.sizePolicy().hasHeightForWidth())
        self.loadAcceptButton.setSizePolicy(sizePolicy4)
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
        self.gamesPage.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.verticalLayout_steamGames = QVBoxLayout(self.gamesPage)
        self.verticalLayout_steamGames.setObjectName(u"verticalLayout_steamGames")
        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.platformLabel = QLabel(self.gamesPage)
        self.platformLabel.setObjectName(u"platformLabel")
        sizePolicy3.setHeightForWidth(self.platformLabel.sizePolicy().hasHeightForWidth())
        self.platformLabel.setSizePolicy(sizePolicy3)
        self.platformLabel.setFont(font)
        self.platformLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_9.addWidget(self.platformLabel)

        self.gamesEmulatorsButton = QPushButton(self.gamesPage)
        self.gamesEmulatorsButton.setObjectName(u"gamesEmulatorsButton")
        sizePolicy.setHeightForWidth(self.gamesEmulatorsButton.sizePolicy().hasHeightForWidth())
        self.gamesEmulatorsButton.setSizePolicy(sizePolicy)

        self.horizontalLayout_9.addWidget(self.gamesEmulatorsButton)

        self.gamesControlsButton = QPushButton(self.gamesPage)
        self.gamesControlsButton.setObjectName(u"gamesControlsButton")
        sizePolicy.setHeightForWidth(self.gamesControlsButton.sizePolicy().hasHeightForWidth())
        self.gamesControlsButton.setSizePolicy(sizePolicy)

        self.horizontalLayout_9.addWidget(self.gamesControlsButton)

        self.horizontalLayout_9.setStretch(0, 2)
        self.horizontalLayout_9.setStretch(1, 1)
        self.horizontalLayout_9.setStretch(2, 1)

        self.verticalLayout_steamGames.addLayout(self.horizontalLayout_9)

        self.scrollAreaGame = QScrollArea(self.gamesPage)
        self.scrollAreaGame.setObjectName(u"scrollAreaGame")
        self.scrollAreaGame.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.scrollAreaGame.setWidgetResizable(True)
        self.scrollAreaGamesContents = QWidget()
        self.scrollAreaGamesContents.setObjectName(u"scrollAreaGamesContents")
        self.scrollAreaGamesContents.setGeometry(QRect(0, 0, 783, 374))
        self.layoutGames = QGridLayout(self.scrollAreaGamesContents)
        self.layoutGames.setObjectName(u"layoutGames")
        self.scrollAreaGame.setWidget(self.scrollAreaGamesContents)

        self.verticalLayout_steamGames.addWidget(self.scrollAreaGame)

        self.horizontalLayout_steamGames_buttons = QHBoxLayout()
        self.horizontalLayout_steamGames_buttons.setObjectName(u"horizontalLayout_steamGames_buttons")
        self.gamesBackButton = QPushButton(self.gamesPage)
        self.gamesBackButton.setObjectName(u"gamesBackButton")
        sizePolicy4.setHeightForWidth(self.gamesBackButton.sizePolicy().hasHeightForWidth())
        self.gamesBackButton.setSizePolicy(sizePolicy4)
        self.gamesBackButton.setMinimumSize(QSize(0, 80))

        self.horizontalLayout_steamGames_buttons.addWidget(self.gamesBackButton)

        self.steamGamesScanButton = QPushButton(self.gamesPage)
        self.steamGamesScanButton.setObjectName(u"steamGamesScanButton")
        sizePolicy4.setHeightForWidth(self.steamGamesScanButton.sizePolicy().hasHeightForWidth())
        self.steamGamesScanButton.setSizePolicy(sizePolicy4)
        self.steamGamesScanButton.setMinimumSize(QSize(0, 80))

        self.horizontalLayout_steamGames_buttons.addWidget(self.steamGamesScanButton)

        self.gamesScanFolderButton = QPushButton(self.gamesPage)
        self.gamesScanFolderButton.setObjectName(u"gamesScanFolderButton")
        sizePolicy4.setHeightForWidth(self.gamesScanFolderButton.sizePolicy().hasHeightForWidth())
        self.gamesScanFolderButton.setSizePolicy(sizePolicy4)
        self.gamesScanFolderButton.setMinimumSize(QSize(0, 80))

        self.horizontalLayout_steamGames_buttons.addWidget(self.gamesScanFolderButton)


        self.verticalLayout_steamGames.addLayout(self.horizontalLayout_steamGames_buttons)

        self.verticalLayout_steamGames.setStretch(0, 1)
        self.verticalLayout_steamGames.setStretch(1, 5)
        self.verticalLayout_steamGames.setStretch(2, 1)
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
        self.scrollAreaExplorerContents.setGeometry(QRect(0, 0, 783, 423))
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
        self.settingsPage = QWidget()
        self.settingsPage.setObjectName(u"settingsPage")
        sizePolicy.setHeightForWidth(self.settingsPage.sizePolicy().hasHeightForWidth())
        self.settingsPage.setSizePolicy(sizePolicy)
        self.verticalLayout_10 = QVBoxLayout(self.settingsPage)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label = QLabel(self.settingsPage)
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_4.addWidget(self.label)

        self.pushButton = QPushButton(self.settingsPage)
        self.pushButton.setObjectName(u"pushButton")
        sizePolicy2.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy2)

        self.horizontalLayout_4.addWidget(self.pushButton)


        self.verticalLayout_10.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.horizontalLayout_6.addItem(self.verticalSpacer_2)


        self.verticalLayout_10.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.horizontalLayout_7.addItem(self.verticalSpacer_3)


        self.verticalLayout_10.addLayout(self.horizontalLayout_7)

        self.settingsBackButton = QPushButton(self.settingsPage)
        self.settingsBackButton.setObjectName(u"settingsBackButton")
        self.settingsBackButton.setMinimumSize(QSize(0, 80))

        self.verticalLayout_10.addWidget(self.settingsBackButton)

        self.stackedWidget.addWidget(self.settingsPage)
        self.emulatorSettingsPage = QWidget()
        self.emulatorSettingsPage.setObjectName(u"emulatorSettingsPage")
        sizePolicy.setHeightForWidth(self.emulatorSettingsPage.sizePolicy().hasHeightForWidth())
        self.emulatorSettingsPage.setSizePolicy(sizePolicy)
        self.verticalLayout_11 = QVBoxLayout(self.emulatorSettingsPage)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.scrollAreaEmulators = QScrollArea(self.emulatorSettingsPage)
        self.scrollAreaEmulators.setObjectName(u"scrollAreaEmulators")
        self.scrollAreaEmulators.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.scrollAreaEmulators.setWidgetResizable(True)
        self.scrollAreaEmulatorsContents = QWidget()
        self.scrollAreaEmulatorsContents.setObjectName(u"scrollAreaEmulatorsContents")
        self.scrollAreaEmulatorsContents.setGeometry(QRect(0, 0, 783, 457))
        self.layoutDynamicEmulators = QVBoxLayout(self.scrollAreaEmulatorsContents)
        self.layoutDynamicEmulators.setObjectName(u"layoutDynamicEmulators")
        self.scrollAreaEmulators.setWidget(self.scrollAreaEmulatorsContents)

        self.verticalLayout_11.addWidget(self.scrollAreaEmulators)

        self.emulatorSettingsBackButton = QPushButton(self.emulatorSettingsPage)
        self.emulatorSettingsBackButton.setObjectName(u"emulatorSettingsBackButton")
        self.emulatorSettingsBackButton.setMinimumSize(QSize(0, 80))

        self.verticalLayout_11.addWidget(self.emulatorSettingsBackButton)

        self.stackedWidget.addWidget(self.emulatorSettingsPage)
        self.navigationPage = QWidget()
        self.navigationPage.setObjectName(u"navigationPage")
        self.navigationPage.setMaximumSize(QSize(801, 561))
        self.verticalLayout_9 = QVBoxLayout(self.navigationPage)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.horizontalLayout_nav_buttons = QHBoxLayout()
        self.horizontalLayout_nav_buttons.setObjectName(u"horizontalLayout_nav_buttons")
        self.btn_nav_back = QPushButton(self.navigationPage)
        self.btn_nav_back.setObjectName(u"btn_nav_back")
        self.btn_nav_back.setMinimumSize(QSize(0, 80))

        self.horizontalLayout_nav_buttons.addWidget(self.btn_nav_back)

        self.btn_nav_save = QPushButton(self.navigationPage)
        self.btn_nav_save.setObjectName(u"btn_nav_save")
        self.btn_nav_save.setMinimumSize(QSize(0, 80))

        self.horizontalLayout_nav_buttons.addWidget(self.btn_nav_save)


        self.verticalLayout_9.addLayout(self.horizontalLayout_nav_buttons)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.btn_nav_joystick = QPushButton(self.navigationPage)
        self.navigationButtons = QButtonGroup(MainWindow)
        self.navigationButtons.setObjectName(u"navigationButtons")
        self.navigationButtons.addButton(self.btn_nav_joystick)
        self.btn_nav_joystick.setObjectName(u"btn_nav_joystick")
        sizePolicy.setHeightForWidth(self.btn_nav_joystick.sizePolicy().hasHeightForWidth())
        self.btn_nav_joystick.setSizePolicy(sizePolicy)
        self.btn_nav_joystick.setCheckable(True)
        self.btn_nav_joystick.setProperty(u"d-pad", False)

        self.horizontalLayout_2.addWidget(self.btn_nav_joystick)

        self.btn_nav_dpad = QPushButton(self.navigationPage)
        self.navigationButtons.addButton(self.btn_nav_dpad)
        self.btn_nav_dpad.setObjectName(u"btn_nav_dpad")
        sizePolicy.setHeightForWidth(self.btn_nav_dpad.sizePolicy().hasHeightForWidth())
        self.btn_nav_dpad.setSizePolicy(sizePolicy)
        self.btn_nav_dpad.setCheckable(True)
        self.btn_nav_dpad.setProperty(u"d-pad", True)

        self.horizontalLayout_2.addWidget(self.btn_nav_dpad)


        self.verticalLayout_9.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_slider_y = QHBoxLayout()
        self.horizontalLayout_slider_y.setObjectName(u"horizontalLayout_slider_y")
        self.label_down = QLabel(self.navigationPage)
        self.label_down.setObjectName(u"label_down")
        self.label_down.setMinimumSize(QSize(70, 0))
        self.label_down.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_slider_y.addWidget(self.label_down)

        self.btn_y_low_minus = QPushButton(self.navigationPage)
        self.btn_y_low_minus.setObjectName(u"btn_y_low_minus")
        sizePolicy.setHeightForWidth(self.btn_y_low_minus.sizePolicy().hasHeightForWidth())
        self.btn_y_low_minus.setSizePolicy(sizePolicy)
        self.btn_y_low_minus.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_slider_y.addWidget(self.btn_y_low_minus)

        self.btn_y_low_plus = QPushButton(self.navigationPage)
        self.btn_y_low_plus.setObjectName(u"btn_y_low_plus")
        sizePolicy.setHeightForWidth(self.btn_y_low_plus.sizePolicy().hasHeightForWidth())
        self.btn_y_low_plus.setSizePolicy(sizePolicy)
        self.btn_y_low_plus.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_slider_y.addWidget(self.btn_y_low_plus)

        self.slider_y = QRangeSlider(self.navigationPage)
        self.slider_y.setObjectName(u"slider_y")
        sizePolicy.setHeightForWidth(self.slider_y.sizePolicy().hasHeightForWidth())
        self.slider_y.setSizePolicy(sizePolicy)

        self.horizontalLayout_slider_y.addWidget(self.slider_y)

        self.btn_y_high_minus = QPushButton(self.navigationPage)
        self.btn_y_high_minus.setObjectName(u"btn_y_high_minus")
        sizePolicy.setHeightForWidth(self.btn_y_high_minus.sizePolicy().hasHeightForWidth())
        self.btn_y_high_minus.setSizePolicy(sizePolicy)
        self.btn_y_high_minus.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_slider_y.addWidget(self.btn_y_high_minus)

        self.btn_y_high_plus = QPushButton(self.navigationPage)
        self.btn_y_high_plus.setObjectName(u"btn_y_high_plus")
        sizePolicy.setHeightForWidth(self.btn_y_high_plus.sizePolicy().hasHeightForWidth())
        self.btn_y_high_plus.setSizePolicy(sizePolicy)
        self.btn_y_high_plus.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_slider_y.addWidget(self.btn_y_high_plus)

        self.label_up = QLabel(self.navigationPage)
        self.label_up.setObjectName(u"label_up")
        self.label_up.setMinimumSize(QSize(70, 0))
        self.label_up.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_slider_y.addWidget(self.label_up)

        self.horizontalLayout_slider_y.setStretch(0, 1)
        self.horizontalLayout_slider_y.setStretch(1, 2)
        self.horizontalLayout_slider_y.setStretch(2, 2)
        self.horizontalLayout_slider_y.setStretch(3, 5)
        self.horizontalLayout_slider_y.setStretch(4, 2)
        self.horizontalLayout_slider_y.setStretch(5, 2)
        self.horizontalLayout_slider_y.setStretch(6, 1)

        self.verticalLayout_9.addLayout(self.horizontalLayout_slider_y)

        self.horizontalLayout_slider_x = QHBoxLayout()
        self.horizontalLayout_slider_x.setObjectName(u"horizontalLayout_slider_x")
        self.label_left = QLabel(self.navigationPage)
        self.label_left.setObjectName(u"label_left")
        self.label_left.setMinimumSize(QSize(70, 0))
        self.label_left.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_slider_x.addWidget(self.label_left)

        self.btn_x_low_minus = QPushButton(self.navigationPage)
        self.btn_x_low_minus.setObjectName(u"btn_x_low_minus")
        sizePolicy.setHeightForWidth(self.btn_x_low_minus.sizePolicy().hasHeightForWidth())
        self.btn_x_low_minus.setSizePolicy(sizePolicy)
        self.btn_x_low_minus.setMaximumSize(QSize(555555, 16777215))

        self.horizontalLayout_slider_x.addWidget(self.btn_x_low_minus)

        self.btn_x_low_plus = QPushButton(self.navigationPage)
        self.btn_x_low_plus.setObjectName(u"btn_x_low_plus")
        sizePolicy.setHeightForWidth(self.btn_x_low_plus.sizePolicy().hasHeightForWidth())
        self.btn_x_low_plus.setSizePolicy(sizePolicy)
        self.btn_x_low_plus.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_slider_x.addWidget(self.btn_x_low_plus)

        self.slider_x = QRangeSlider(self.navigationPage)
        self.slider_x.setObjectName(u"slider_x")
        sizePolicy.setHeightForWidth(self.slider_x.sizePolicy().hasHeightForWidth())
        self.slider_x.setSizePolicy(sizePolicy)

        self.horizontalLayout_slider_x.addWidget(self.slider_x)

        self.btn_x_high_minus = QPushButton(self.navigationPage)
        self.btn_x_high_minus.setObjectName(u"btn_x_high_minus")
        sizePolicy.setHeightForWidth(self.btn_x_high_minus.sizePolicy().hasHeightForWidth())
        self.btn_x_high_minus.setSizePolicy(sizePolicy)
        self.btn_x_high_minus.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_slider_x.addWidget(self.btn_x_high_minus)

        self.btn_x_high_plus = QPushButton(self.navigationPage)
        self.btn_x_high_plus.setObjectName(u"btn_x_high_plus")
        sizePolicy.setHeightForWidth(self.btn_x_high_plus.sizePolicy().hasHeightForWidth())
        self.btn_x_high_plus.setSizePolicy(sizePolicy)
        self.btn_x_high_plus.setMaximumSize(QSize(16777215, 16777215))

        self.horizontalLayout_slider_x.addWidget(self.btn_x_high_plus)

        self.label_right = QLabel(self.navigationPage)
        self.label_right.setObjectName(u"label_right")
        self.label_right.setMinimumSize(QSize(70, 0))
        self.label_right.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_slider_x.addWidget(self.label_right)

        self.horizontalLayout_slider_x.setStretch(0, 1)
        self.horizontalLayout_slider_x.setStretch(1, 2)
        self.horizontalLayout_slider_x.setStretch(2, 2)
        self.horizontalLayout_slider_x.setStretch(3, 5)
        self.horizontalLayout_slider_x.setStretch(4, 2)
        self.horizontalLayout_slider_x.setStretch(5, 2)
        self.horizontalLayout_slider_x.setStretch(6, 1)

        self.verticalLayout_9.addLayout(self.horizontalLayout_slider_x)

        self.verticalLayout_9.setStretch(0, 1)
        self.verticalLayout_9.setStretch(1, 3)
        self.verticalLayout_9.setStretch(2, 4)
        self.verticalLayout_9.setStretch(3, 4)
        self.stackedWidget.addWidget(self.navigationPage)

        self.verticalLayout_6.addWidget(self.stackedWidget)


        self.verticalLayout.addLayout(self.verticalLayout_6)

        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 7)

        self.horizontalLayout.addLayout(self.verticalLayout)

        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 4)

        self.verticalLayout_8.addLayout(self.horizontalLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1032, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(2)
        self.stackedWidgetAcciones.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.videoLabel.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.controllerImage.setText("")
        self.pipButton.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.stopButton.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.label_platforms_title.setText(QCoreApplication.translate("MainWindow", u"CAT\u00c1LOGO DE JUEGOS", None))
        self.emulatorsButton.setText(QCoreApplication.translate("MainWindow", u"Emuladores", None))
        self.controlsButton.setText(QCoreApplication.translate("MainWindow", u"Controles", None))
        self.scrollAreaPlaforms.setStyleSheet(QCoreApplication.translate("MainWindow", u"QScrollArea { border: none; background: transparent; } QWidget#scrollAreaGamesContents { background: transparent; }", None))
        self.gamesScanButton.setText(QCoreApplication.translate("MainWindow", u"\U0001f50d ESCANEAR STEAM", None))
        self.scanFolderButton.setText(QCoreApplication.translate("MainWindow", u"\U0001f4c1 A\U000000d1ADIR CARPETA", None))
        self.gesturesBackButton.setText(QCoreApplication.translate("MainWindow", u"\u25c0 Volver  sin guardar", None))
        self.gesturesBackButton.setProperty(u"type", "")
        self.gesturesSaveLocalButton.setText(QCoreApplication.translate("MainWindow", u"Guardar", None))
        self.gesturesSaveLocalButton.setProperty(u"type", QCoreApplication.translate("MainWindow", u"primary", None))
        self.gesturesSaveExternalButton.setText(QCoreApplication.translate("MainWindow", u"Guardar Como", None))
        self.gesturesLoadButton.setText(QCoreApplication.translate("MainWindow", u"Cargar archivo", None))
        self.pushButton_21.setText(QCoreApplication.translate("MainWindow", u"Morritos", None))
        self.pushButton_21.setProperty(u"gesture", QCoreApplication.translate("MainWindow", u"mouthPucker", None))
        self.pushButton_20.setText(QCoreApplication.translate("MainWindow", u"Sonrisa", None))
        self.pushButton_20.setProperty(u"gesture", QCoreApplication.translate("MainWindow", u"smile", None))
        self.pushButton_18.setText(QCoreApplication.translate("MainWindow", u"Gui\u00f1o", None))
        self.pushButton_18.setProperty(u"gesture", QCoreApplication.translate("MainWindow", u"eyeBlinkRight", None))
        self.pushButton_19.setText(QCoreApplication.translate("MainWindow", u"Cejas", None))
        self.pushButton_19.setProperty(u"gesture", QCoreApplication.translate("MainWindow", u"eyeBrowsUp", None))
        self.pushButton_22.setText(QCoreApplication.translate("MainWindow", u"Abrir boca", None))
        self.pushButton_22.setProperty(u"gesture", QCoreApplication.translate("MainWindow", u"jawOpen", None))
        self.noseButton.setText(QCoreApplication.translate("MainWindow", u"Nariz", None))
        self.controlsCancelButton.setText(QCoreApplication.translate("MainWindow", u"\u25c0 VOLVER", None))
        self.controlsSaveButon.setText(QCoreApplication.translate("MainWindow", u"\u2714 GUARDAR Y VOLVER", None))
        self.controlsSaveButon.setProperty(u"type", QCoreApplication.translate("MainWindow", u"primary", None))
        self.controlsCleanButton.setText(QCoreApplication.translate("MainWindow", u"Vaciar", None))
        self.gestureLabel.setText(QCoreApplication.translate("MainWindow", u"Gesto", None))
        self.btn_cat_mando.setText(QCoreApplication.translate("MainWindow", u"\U0001f3ae BOT\U000000d3N DEL MANDO", None))
        self.btn_cat_sys.setText(QCoreApplication.translate("MainWindow", u"\u2699\ufe0f ACCI\u00d3N DE SISTEMA", None))
        self.btn_volver_cat1.setText(QCoreApplication.translate("MainWindow", u"\u25c0  CAMBIAR TIPO DE ACCI\u00d3N", None))
        self.btn_volver_cat1.setProperty(u"type", QCoreApplication.translate("MainWindow", u"secondary", None))
        self.Y_button.setText(QCoreApplication.translate("MainWindow", u"Y", None))
        self.Y_button.setProperty(u"gamepadInput", QCoreApplication.translate("MainWindow", u"XUSB_GAMEPAD_Y", None))
        self.X_button.setText(QCoreApplication.translate("MainWindow", u"X", None))
        self.X_button.setProperty(u"gamepadInput", QCoreApplication.translate("MainWindow", u"XUSB_GAMEPAD_X", None))
        self.Select_button.setText(QCoreApplication.translate("MainWindow", u"Select", None))
        self.Select_button.setProperty(u"gamepadInput", QCoreApplication.translate("MainWindow", u"XUSB_GAMEPAD_BACK", None))
        self.A_button.setText(QCoreApplication.translate("MainWindow", u"A", None))
        self.A_button.setProperty(u"gamepadInput", QCoreApplication.translate("MainWindow", u"XUSB_GAMEPAD_A", None))
        self.B_button.setText(QCoreApplication.translate("MainWindow", u"B", None))
        self.B_button.setProperty(u"gamepadInput", QCoreApplication.translate("MainWindow", u"XUSB_GAMEPAD_B", None))
        self.Start_button.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.Start_button.setProperty(u"gamepadInput", QCoreApplication.translate("MainWindow", u"XUSB_GAMEPAD_START", None))
        self.L2_button.setText(QCoreApplication.translate("MainWindow", u"L2", None))
        self.L2_button.setProperty(u"gamepadInput", QCoreApplication.translate("MainWindow", u"XUSB_GAMEPAD_L2", None))
        self.R1_button.setText(QCoreApplication.translate("MainWindow", u"R1", None))
        self.R1_button.setProperty(u"gamepadInput", QCoreApplication.translate("MainWindow", u"XUSB_GAMEPAD_R1", None))
        self.R2_button.setText(QCoreApplication.translate("MainWindow", u"R2", None))
        self.R2_button.setProperty(u"gamepadInput", QCoreApplication.translate("MainWindow", u"XUSB_GAMEPAD_R2", None))
        self.L1_button.setText(QCoreApplication.translate("MainWindow", u"L1", None))
        self.L1_button.setProperty(u"gamepadInput", QCoreApplication.translate("MainWindow", u"XUSB_GAMEPAD_L1", None))
        self.btn_volver_cat2.setText(QCoreApplication.translate("MainWindow", u"\u25c0  CAMBIAR TIPO DE ACCI\u00d3N", None))
        self.btn_volver_cat2.setProperty(u"type", QCoreApplication.translate("MainWindow", u"secondary", None))
        self.btn_sys_modo.setText(QCoreApplication.translate("MainWindow", u"Cambiar Modo Movimiento", None))
        self.btn_sys_modo.setProperty(u"gamepadInput", QCoreApplication.translate("MainWindow", u"SYS_CHANGE_MODE", None))
        self.btn_sys_enter.setText(QCoreApplication.translate("MainWindow", u"Click", None))
        self.btn_sys_enter.setProperty(u"gamepadInput", QCoreApplication.translate("MainWindow", u"SYS_NAV_ENTER", None))
        self.btn_sys_restore.setText(QCoreApplication.translate("MainWindow", u"Restaurar", None))
        self.btn_sys_restore.setProperty(u"gamepadInput", QCoreApplication.translate("MainWindow", u"SYS_RESTORE_APP", None))
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
        self.platformLabel.setText(QCoreApplication.translate("MainWindow", u"CAT\u00c1LOGO DE JUEGOS", None))
        self.gamesEmulatorsButton.setText(QCoreApplication.translate("MainWindow", u"Emuladores", None))
        self.gamesControlsButton.setText(QCoreApplication.translate("MainWindow", u"Controles", None))
        self.scrollAreaGame.setStyleSheet(QCoreApplication.translate("MainWindow", u"QScrollArea { border: none; background: transparent; } QWidget#scrollAreaSteamGamesContents { background: transparent; }", None))
        self.gamesBackButton.setText(QCoreApplication.translate("MainWindow", u"\u25c0 VOLVER AL MEN\u00da", None))
        self.steamGamesScanButton.setText(QCoreApplication.translate("MainWindow", u"\U0001f50d ESCANEAR STEAM", None))
        self.gamesScanFolderButton.setText(QCoreApplication.translate("MainWindow", u"\U0001f4c1 ESCANEAR CARPETA", None))
        self.label_explorer_path.setText(QCoreApplication.translate("MainWindow", u"Ruta actual: C:\\", None))
        self.scrollAreaExplorer.setStyleSheet(QCoreApplication.translate("MainWindow", u"QScrollArea { border: none; background: transparent; } QWidget#scrollAreaExplorerContents { background: transparent; }", None))
        self.explorerCancelButton.setText(QCoreApplication.translate("MainWindow", u"\u274c CANCELAR", None))
        self.explorerUpButton.setText(QCoreApplication.translate("MainWindow", u"\u2b06 SUBIR NIVEL", None))
        self.explorerSelectButton.setText(QCoreApplication.translate("MainWindow", u"\u2705 ELEGIR ESTA CARPETA", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"ROMS:", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Cambiar emulador", None))
        self.settingsBackButton.setText(QCoreApplication.translate("MainWindow", u"\u25c0 VOLVER AL MEN\u00da", None))
        self.settingsBackButton.setProperty(u"type", QCoreApplication.translate("MainWindow", u"secondary", None))
        self.scrollAreaEmulators.setStyleSheet(QCoreApplication.translate("MainWindow", u"QScrollArea { border: none; background: transparent; } QWidget#scrollAreaEmulatorsContents { background: transparent; }", None))
        self.emulatorSettingsBackButton.setText(QCoreApplication.translate("MainWindow", u"\u25c0 VOLVER A AJUSTES", None))
        self.emulatorSettingsBackButton.setProperty(u"type", QCoreApplication.translate("MainWindow", u"secondary", None))
        self.btn_nav_back.setText(QCoreApplication.translate("MainWindow", u"\u25c0 VOLVER AL MEN\u00da", None))
        self.btn_nav_back.setProperty(u"type", QCoreApplication.translate("MainWindow", u"secondary", None))
        self.btn_nav_save.setText(QCoreApplication.translate("MainWindow", u"\u2714 GUARDAR", None))
        self.btn_nav_save.setProperty(u"type", QCoreApplication.translate("MainWindow", u"primary", None))
        self.btn_nav_joystick.setText(QCoreApplication.translate("MainWindow", u"\U0001f579\U0000fe0f MODO JOYSTICK", None))
        self.btn_nav_dpad.setText(QCoreApplication.translate("MainWindow", u"\U0001f3ae MODO D-PAD", None))
        self.label_down.setText(QCoreApplication.translate("MainWindow", u"Abajo", None))
        self.btn_y_low_minus.setText(QCoreApplication.translate("MainWindow", u"\u2796", None))
        self.btn_y_low_plus.setText(QCoreApplication.translate("MainWindow", u"\u2795", None))
        self.btn_y_high_minus.setText(QCoreApplication.translate("MainWindow", u"\u2796", None))
        self.btn_y_high_plus.setText(QCoreApplication.translate("MainWindow", u"\u2795", None))
        self.label_up.setText(QCoreApplication.translate("MainWindow", u"Arriba", None))
        self.label_left.setText(QCoreApplication.translate("MainWindow", u"Izquierda", None))
        self.btn_x_low_minus.setText(QCoreApplication.translate("MainWindow", u"\u2796", None))
        self.btn_x_low_plus.setText(QCoreApplication.translate("MainWindow", u"\u2795", None))
        self.btn_x_high_minus.setText(QCoreApplication.translate("MainWindow", u"\u2796", None))
        self.btn_x_high_plus.setText(QCoreApplication.translate("MainWindow", u"\u2795", None))
        self.label_right.setText(QCoreApplication.translate("MainWindow", u"Derecha", None))
    # retranslateUi


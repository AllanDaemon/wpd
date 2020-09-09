import QtQuick 2.13
import QtQuick.Window 2.13
import QtQuick.Controls 2.13
import QtQuick.Controls.Material 2.0

ApplicationWindow {
	id: root
	visible: true
	width: 640 * 1.7
	height: 480 * 1.3

	Component.onCompleted: {
		setX(Screen.width / 2 - width / 2);
		setY(Screen.height / 2 - height / 2);
		console.info("INFO == STARTED")
	}

	//color: '#111'

	title: qsTr("Wallpper Picture of the Day")

	header: TopMenu {
//		height: 40
	}

	Galery {
		anchors.fill: parent
	}



}

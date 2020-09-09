import QtQuick 2.13
import QtQuick.Window 2.13

Window {
	visible: true
	width: 640 * 1.7
	height: 480 * 1.3

	title: qsTr("Picture of the Day")

	Component.onCompleted: {
			setX(Screen.width / 2 - width / 2);
			setY(Screen.height / 2 - height / 2);
	}
}

import QtQuick 2.0
import QtQuick.Controls 2.13
import QtQuick.Layouts 1.3

ToolBar {
	id: toolbar
	height: refresh_button.height

	RowLayout {
		anchors.fill: parent

		Label {
			text: "Source:"
			leftPadding: 10
		}

		ComboBox {
			id: comboBox
			wheelEnabled: true

			model: ["Nasa", "Bing", "Wikipedia"]

			onHighlighted: console.info("Hightlighted:", index)
		}

		ToolButton {
			text: qsTr("Reload")
			display: AbstractButton.IconOnly
			icon.source: "qrc:/assets/view-refresh.svg"

			onClicked: console.info("RELOADED btn")
		}

		Item { Layout.fillWidth: true }

		ToolButton {
			text: qsTr("Settings")
			display: AbstractButton.IconOnly
			icon.source: "qrc:/assets/settings-configure.svg"

			//onClicked: menu.open()
		}
	}
}

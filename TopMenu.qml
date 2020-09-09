import QtQuick 2.0
import QtQuick.Controls 2.13
import QtQuick.Layouts 1.3

ToolBar {
	id: toolbar
	height: refresh_button.height

	RowLayout {
		anchors.leftMargin: 20
		anchors.rightMargin: 20
		anchors.fill: parent
		spacing: 5

		Label {
			text: "Source:"
		}

		ComboBox {
			id: comboBox
			wheelEnabled: true

			model: ["Nasa", "Bing", "Wikipedia"]

			onHighlighted: console.info("Hightlighted:", index)
		}

		ToolButton {
			id: refresh_button
			text: qsTr("Reload")

			icon.height: 32
			icon.width: 32
			icon.source: "qrc:/assets/view-refresh.svg"
			display: AbstractButton.IconOnly

			onClicked: console.info("RELOADED btn")
		}

		Item { Layout.fillWidth: true }

		ToolButton {
			text: qsTr("⋮ Settings")
			//onClicked: menu.open()
		}
	}
}

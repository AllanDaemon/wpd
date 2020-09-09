import QtQuick 2.0
import QtQuick.Controls 2.13
import QtQuick.Layouts 1.3

ToolBar {
	id: toolbar
	height: 32

	 RowLayout {
		 anchors.fill: parent

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
			text: qsTr("Reload")
			onClicked: console.log("RELOADED btn")
		}

		ToolButton {
			text: qsTr("⋮")
			//onClicked: menu.open()
		}
	}
}

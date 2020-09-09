import QtQuick 2.0
import QtQuick.XmlListModel 2.0
import QtQuick.Controls 2.13


GridView {
	id: galery
	anchors.fill: parent
	anchors.margins: 10
	cellHeight: 250
	cellWidth: 210

	property string cachePath: 'file:///home/rea/code/wpd/cache'

	delegate: cardview

	model: galerymodel


	XmlListModel {
		id: galerymodel
		source: cachePath + "/bing.data.xml"
		query: "/*/*"

		 XmlRole { name: "ititle"; query: "headline/string()" }
		 XmlRole { name: "date"; query: "startdate/string()" }
		 XmlRole { name: "url"; query: "cache/string()" }
	}

	ListModel {
		id: galerymodelstatic
		ListElement {date: "2020-09-01"}
		ListElement {date: "2020-09-02"}
		ListElement {date: "2020-09-03"}
		ListElement {date: "2020-09-04"}
		ListElement {date: "2020-09-05"}
		ListElement {date: "2020-09-06"}
		ListElement {date: "2020-09-07"}
		ListElement {date: "2020-09-08"}
		ListElement {date: "2020-09-09"}
		ListElement {date: "2020-09-10"}
	}


	Component {
		id: cardview

		Rectangle {
			id: wrapper
			color: '#AAA'
			width: 200
			height: 200

			Column {
				anchors.fill: parent
				spacing: 5

				Rectangle {
					color: "#F88"
					width: parent.width
					height: datetxt.height
					Text {
						id: datetxt
						text: date
						width: parent.width
					}
				}

				Rectangle {
					color: "#8F8"
					width: parent.width
					height: parent.width * 0.5625
					Image {
						id: img
						source: cachePath + "/" + url
						fillMode: Image.PreserveAspectFit
						width: parent.width
					}
				}

				Rectangle {
					color: "#88F"
					width: parent.width
					height: titletxt.height
					Text {
						id: titletxt
						text: ititle
						width: parent.width
						wrapMode: Text.Wrap
						height: 80
					}
				}

			}


			MouseArea {
				id: card_area
				anchors.fill: parent
				hoverEnabled: true
			}

			ToolTip {
				visible: card_area.containsMouse
				text: ititle
				delay: 420
			}
		}
	}
}

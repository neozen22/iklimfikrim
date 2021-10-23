
import Editor from './ckeditor'

let saveeditor;
//ckeditor config
Editor
				.create( document.querySelector( '.editor' ), {
					alignment: {
						options: [ 'left', 'center','right' ]
					},
					
				toolbar: {
					items: [
						'heading',
						'|',
						'bold',
						'italic',
						'link',
						'bulletedList',
						'numberedList',
						'|',
						'outdent',
						'indent',
						'|',
						'imageInsert',
						'imageUpload',
						'blockQuote',
						'insertTable',
						'mediaEmbed',
						'undo',
						'redo',
						'fontFamily',
						'fontColor',
						'fontSize',
						'specialCharacters',
						'alignment'
					]
				},
				language: 'tr',
				image: {
					toolbar: [
						'imageTextAlternative',
						'imageStyle:inline',
						'imageStyle:block',
						'imageStyle:side'
					]
				},
				table: {
					contentToolbar: [
						'tableColumn',
						'tableRow',
						'mergeTableCells'
					]
				},
					licenseKey: '',
					
					
					
				} )
				.then( editor => {
					window.editor = editor;
					saveeditor = editor;
					
					
				} )
				.catch( error => {
					console.error( 'Oops, something went wrong!' );
					console.error( 'Please, report the following error on https://github.com/ckeditor/ckeditor5/issues with the build id and the error stack trace:' );
					console.warn( 'Build id: uhco37i9tu3m-7de0kr79gr7' );
					console.error( error );
				} );

				$( '#article-save-button' ).on( 'click', function() {

					const editorData = editor.getData();
					$.post("/edit", {
                        article_data : JSON.stringify(editorData)
                    })
                    console.log(editorData)
                })
# CHANGE_FLAG: This is a new file
from notebook.services.contents.filemanager import FileContentsManager
from contextlib import contextmanager
from tornado import web
import base64
import os, io

class LargeFileManager(FileContentsManager):

    def save(self, model, path=''):
        """Save the file model and return the model with no content."""
        chunk = model.get("chunk", None)
        if chunk is not None and model['type'] in ['notebook', 'file']:
            path = path.strip('/')
            if 'type' not in model:
                raise web.HTTPError(400, u'No file type provided')
            if 'content' not in model and model['type'] != 'directory':
                raise web.HTTPError(400, u'No file content provided')
            os_path = self._get_os_path(path)
            # First chunk
            if chunk == 1:
                self.log.debug("Saving %s", os_path)
                self.run_pre_save_hook(model=model, path=path)
            try:
                # First chunk
                if chunk == 1:
                    super(LargeFileManager, self)._save_file(os_path, model['content'], model.get('format'))
                else:
                    self._save_large_file(os_path, model['content'], model.get('format'))
                # Last chunk
                if chunk == -1:
                    if model['type'] == 'notebook':
                        # One checkpoint should always exist for notebooks.
                        if not self.checkpoints.list_checkpoints(path):
                            self.create_checkpoint(path)
            except web.HTTPError:
                raise
            except Exception as e:
                self.log.error(u'Error while saving file: %s %s', path, e, exc_info=True)
                raise web.HTTPError(500, u'Unexpected error while saving file: %s %s' % (path, e))
            # Last chunk
            validation_message = None
            if model['type'] == 'notebook':
                self.validate_notebook_model(model)
                validation_message = model.get('message', None)

            model = self.get(path, content=False)
            if validation_message:
                model['message'] = validation_message

            if chunk == -1:
                self.run_post_save_hook(model=model, os_path=os_path)
            return model
        else:
            return super(LargeFileManager, self).save(model, path)

    def _save_large_file(self, os_path, content, format):
        """Save content of a generic file."""
        if format not in {'text', 'base64'}:
            raise web.HTTPError(
                400,
                "Must specify format of file contents as 'text' or 'base64'",
            )
        try:
            if format == 'text':
                bcontent = content.encode('utf8')
            else:
                b64_bytes = content.encode('ascii')
                bcontent = base64.decodestring(b64_bytes)
        except Exception as e:
            raise web.HTTPError(
                400, u'Encoding error saving %s: %s' % (os_path, e)
            )

        with self.simple_appending(os_path, text=False) as f:
            f.write(bcontent)

    @contextmanager
    def simple_appending(self, os_path, *args, **kwargs):
        """wrapper around atomic_writing that turns permission errors to 403.
        Depending on flag 'use_atomic_writing', the wrapper perform an actual atomic writing or
        simply writes the file (whatever an old exists or not)"""
        # import pdb; pdb.set_trace()
        with self.perm_to_403(os_path):
            with _simple_appending(os_path, *args, log=self.log, **kwargs) as f:
                yield f


@contextmanager
def _simple_appending(path, text=True, encoding='utf-8', log=None, **kwargs):
    """Context manager to write file without doing atomic writing
    ( for weird filesystem eg: nfs).
    Parameters
    ----------
    path : str
        The target file to write to.
    text : bool, optional
        Whether to open the file in text mode (i.e. to write unicode). Default is
        True.
    encoding : str, optional
        The encoding to use for files opened in text mode. Default is UTF-8.
    **kwargs
        Passed to :func:`io.open`.
    """
    # realpath doesn't work on Windows: http://bugs.python.org/issue9949
    # Luckily, we only need to resolve the file itself being a symlink, not
    # any of its directories, so this will suffice:
    if os.path.islink(path):
        path = os.path.join(os.path.dirname(path), os.readlink(path))

    if text:
        # Make sure that text files have Unix linefeeds by default
        kwargs.setdefault('newline', '\n')
        fileobj = io.open(path, 'a', encoding=encoding, **kwargs)
    else:
        fileobj = io.open(path, 'ab', **kwargs)

    try:
        yield fileobj
    except:
        fileobj.close()
        raise

        fileobj.close()

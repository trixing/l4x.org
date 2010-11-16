__version__ = '0.6'
__author__ = 'Jan-Wijbrand Kolmanm <jw at n--tree dot net>'

"""
Copyright 2005 Jan-Wijbrand Kolmanm <jw at n--tree dot net>

Portico, a Pyblosxom plugin for entry based photo galleries.

  Recognized entry fields:
  
    [entry]
    title: <the blog entry's title, required>
    thumbnails: <number of thumbnails to display for this entry, optional>
    cherries: <space separated list of entry numbers to display, optional>
  
  Recognized image fields:
  
    [<entry title>]
    image: <URL to resized version of image, required>
    thumbnail: <URL to thumbnail version of image, required>

  CSS classes used in the default templates:
  
    div.gallery  (from the main template)
    
      div.curtain  (from the single image template)
      div.slide  (from the single image template)
        div.prev-next-links  (from the single image template)
          a.prev  (from the single image template)
          a.back  (from the single image template)
          a.next  (from the single image template)
        div.image  (from the single image template)
        
      div.thumbnail  (from the thumbnail template)
      
    div.clearer  (from the main template)
    
  Available config options:

    # Blog-wide setting for the number of
    # thumbnails displayed whenever the blog entry
    # is not rendered at its permanent URL.
    py['portico_thumbs'] = 6

    # Template used when displaying one single image
    # (usually the 'resized', or 'preview' version of
    # a photo). 
    py['portico_single_image_template'] = '''
      <div class="curtain">&nbsp;</div>
      <div class="slide">
        <div class="prev-next-links">
          <a class="prev" href="%(prevlink)s">prev</a>
          <a class="back" href="%(backlink)s">back</a>
          <a class="next" href="%(nextlink)s">next</a>
        </div>
        <div class="image">
          <img src="%(imagesrc)s"/>
        </div>
      </div>
      '''

    # Main template for the blog entry, rendering the
    # gallery of thumbnails.
    py['portico_gallery_main_template'] = '''
      <div class="gallery">
        %(thumbnails)s
      </div>
      %(morelink)s
      <div class="clearer"></div>
      '''
    
    # Template used for the 'more' link, pointing to
    # the permanent URL for the entry.
    py['portico_more_template'] = '''
      <a href="%(morelink)s">more</a>
      '''
    
    # Template used for rendering one single thumbnail
    # within the gallaery of thumbnails.
    py['portico_thumbnail_template'] = '''
      <div class="thumbnail">
        <a href="%(singleimagelink)s"
          <img src="%(imagesrc)s"/>
        </a>
      </div>
      '''
          
License:

  Permission is hereby granted, free of charge, to any person obtaining a
  copy of this software and associated documentation files (the "Software"),
  to deal in the Software without restriction, including without limitation
  the rights to use, copy, modify, merge, publish, distribute, sublicense,
  and/or sell copies of the Software, and to permit persons to whom the
  Software is furnished to do so, subject to the following conditions:
   
  The above copyright notice and this permission notice shall be included in
  all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
  DEALINGS IN THE SOFTWARE.
"""

def verify_installation(request):
    config = request.getConfiguration()
    mapper = config.get('portico_url_mapper', None)
    if mapper is None:
        return True # no url mapper defined, that's ok, it's optional anyway
    if not callable(mapper):
        # there's a mapper name defined which should be importable then
        try:
            if '.' in mapper:
                # see if we can import the mapper
                m = __import__(mapper)
            else:
                # no dots, look it up in the global namespace
                m = globals().get(mapper)
        except ImportError:
            print 'Cannot import URL mapper %s' % m
            return False
    else:            
        # there's a URL mapper defined, see if it implements the mapper contract
        m = mapper()
        
    valid = True
    image_method = getattr(m, 'image', None)
    if image_method is None or not callable(image_method):
        print 'An URL mapper is required to implement an \'image\' method'
        valid = False
    thumbnail_method = getattr(m, 'thumbnail', None)
    if thumbnail_method is None or not callable(thumbnail_method):
        print 'An URL mapper is required to implement a \'thumbnail\' method'
        valid = False
    return valid

def cb_entryparser(args):
    args['port'] = portico
    return args

_THUMBS = 5

_SINGLE_IMAGE_TEMPLATE = """
  <div class="curtain">&nbsp;</div>
  <div class="slide">
    <div class="prev-next-links">
      <a class="prev" href="%(prevlink)s">prev</a>
      <a class="back" href="%(backlink)s">back</a>
      <a class="next" href="%(nextlink)s">next</a>
    </div>
    <div class="image">
      <img src="%(imagesrc)s"/>
    </div>
  </div>
  """

_GALLERY_MAIN_TEMPLATE = """
  <div class="gallery">
    %(thumbnails)s
  </div>
  %(morelink)s
  <div class="clearer"></div>
  """
    
_MORE_TEMPLATE = """
  <a href="%(morelink)s">more</a>
  """
    
_THUMBNAIL_TEMPLATE = """
  <div class="thumbnail">
    <a href="%(singleimagelink)s"
      <img src="%(imagesrc)s"/>
    </a>
  </div>
  """  
    
_config = {} # global dict that'll contain the blog configuration.
_mapper = None # global reference to URL mapper used.
  
def _entry(title, body):
    return {"body": body, "title": title}      
        
def portico(filename, request):

    global _config
    _config = config = request.getConfiguration()
    
    # XXX this is so ugly...
    import os.path
    path = filename[len(config['datadir']):]
    path, ext = os.path.splitext(path)
    entry_url = config['base_url'] + path

    from ConfigParser import ConfigParser
    cp = ConfigParser()
    cp.readfp(open(filename))
    entry = Entry(cp, entry_url)
    
    global _mapper
    mapper = entry.metadata.get(
        'mapper', config.get('portico_url_mapper', None))
    if mapper is not None:
        if callable(mapper):
            _mapper = mapper()
        elif '.' in mapper:
            # see if we can import the mapper
            _mapper = __import__(mapper)
        else:
            # no dots, look it up in the global namespace
            _mapper = globals().get(mapper)
    
    if request.getData()['bl_type'] == 'file': # we're at a leaf
        photo_idx = request.getForm().getvalue('idx', None)
        if photo_idx is not None:
            idx = int(photo_idx)
            renderer = SingleImageGallery(entry, idx)
        else:
            renderer = Gallery(entry)
        return _entry(entry.title, renderer())
    
    if entry.metadata.has_key('cherries'): 
        # render a particular sub-selection of the thumbs
        # (the 'cherries').
        idxs = [int(idx)-1 for idx in entry.metadata['cherries'].split()]
        renderer = PreviewGallery(entry, idxs)
        return _entry(entry.title, renderer())

    # render just the starting so many of the thumbs.
    # (first look in metadata, then global config or
    # fallback on default <_THUMBS>)
    max = int(
        entry.metadata.get('thumbs', config.get('portico_thumbs', _THUMBS)))
    renderer = PreviewGallery(entry, range(max))      
    return _entry(entry.title, renderer())

class Entry:
    
    def __init__(self, data, url):
        self.url = url
        sections = [s for s in data.sections() if s != 'entry']
        sections.sort()
        self._images = [Image(data, section) for section in sections]
        self.metadata = {}
        for option in data.options('entry'):
            if option == 'title':
                self.title = data.get('entry', 'title')
                continue
            self.metadata[option] = data.get('entry', option)
            
    def __len__(self):
        return len(self._images)
    
    def __getitem__(self, idx):
        return self._images[idx]
    
    def __iter__(self):
        return iter(self._images)

class Image:
    
    def __init__(self, data, section):
        self._data = data
        self._section = section
        self._options = data.options(section)

    def _image(self):
         # there should be an image option.
        url = self._data.get(self._section, 'image')
        if _mapper is None:
            return url
        return _mapper.image(url)
    image = property(_image)
    
    def _thumbnail(self):
        if _mapper is None:
            # have to asume there's a thumbnail option for this image if there's
            # no mapper available.
            return self._data.get(self._section, 'thumbnail')
         # there should be an image option.
        return _mapper.thumbnail(self._data.get(self._section, 'image'))
    thumbnail = property(_thumbnail)
        
    def __getattr__(self, name):
        if name not in self._options:
            raise AttributeError, 'Unknown attribute %s' % name
        return self._data.get(self._section, name)
        
class SingleImageGallery:

    def __init__(self, entry, idx):
        self.entry = entry
        self.idx = idx
        self.url = entry[idx].image

    def __call__(self):
        hasprev = self.idx > 0 and len(self.entry) > 1
        hasnext = self.idx < len(self.entry) - 1
        interpolation = {
            'backlink': self.entry.url,
            'prevlink': hasprev and '%s?idx=%s'%(self.entry.url, self.idx-1) or '',
            'nextlink': hasnext and '%s?idx=%s'%(self.entry.url, self.idx+1) or '',
            'imagesrc': self.url,
            }
        template = _config.get(
            'portico_single_image_template', _SINGLE_IMAGE_TEMPLATE)
        return template % interpolation

class Gallery:
    
    def __init__(self, entry):
        self.entry = entry
        self.urls = [image.thumbnail for image in entry]
        
    def __call__(self):
        interpolation = {
            'thumbnails': self._renderImages(),
            'morelink': self._moreLink()}
        template = _config.get(
            'portico_gallery_main_template', _GALLERY_MAIN_TEMPLATE)
        return template % interpolation
        
    def _renderImages(self):
        images = []
        for url in self.urls:
            images.append(self._renderImage(url))
        return '\n'.join(images)

    def _renderImage(self, url):
        interpolation = {
            'singleimagelink': '%s?idx=%s'%(self.entry.url, self.urls.index(url)),
            'imagesrc': url}
        template = _config.get(
            'portico_thumbnail_template', _THUMBNAIL_TEMPLATE)
        return template % interpolation
            
    def _moreLink(self):
        return ''
        
class PreviewGallery(Gallery):
    
    def __init__(self, entry, idxs):
        self.entry = entry
        self.urls = []
        for idx in idxs:
            try:
                self.urls.append(entry[idx].thumbnail)
            except IndexError, e:
                continue
        
    def _moreLink(self):
        interpolation = {'morelink': self.entry.url}
        template = _config.get('portico_more_template', _MORE_TEMPLATE)
        return template % interpolation

class _Gallery2Mapper:
    """Implements the minimal implicit contract for URL mappers.
    """
    
    def image(self, url):
        return url
      
    def thumbnail(self, url):
        return url.replace('resized', 'thumbnails')
    
gallery2mapper = _Gallery2Mapper()
""" Framework for building re-usable web applications

    You can use and redistribute this module under conditions of the
    GNU General Public License that can be found either at
    [ http://www.gnu.org/ ] or in file "LICENSE" contained in the
    distribution tarball of this module.

    Copyright (c) 2004 Anders Pearson, anders@columbia.edu
    
    @name           cgi_app
    @version        1.3
    @author-name    Anders Pearson
    @author-email   anders@columbia.edu
    @website        http://thraxil.org/code/cgi_app/
    @license-name   GNU GPL
    @license-url    http://www.gnu.org/licenses/gpl.html


"""

import os,cgi,sys
from types import *
from Cookie import SimpleCookie  
try:
    from mod_python import apache, util
    from mod_python import Cookie
except:
    pass

__version__ = 1.3
__author__  = "Anders Pearson <anders@columbia.edu>"

class CGI_Application:
    """ Abstract class that provides basic functionality for a web
    application.

    To use, you should subclass CGI_Application and override setup() and
    teardown() (if necessary) and define your run modes. 
    """
    
    def __init__(self,req=None, form=None):
        self.req = req
        if self.req != None:
            # mod_python
            self.form = util.FieldStorage(self.req)
            self._cookies_in = Cookie.get_cookies(self.req)
        else:
            # if we have a form, don't get a new one
            if form:
               self.form=form
            # if we don't have a form, then get one
            else:
               self.form = cgi.FieldStorage()
            self._cookies_in = SimpleCookie()
            try:
                self._cookies_in.load(os.environ["HTTP_COOKIE"])
            except KeyError:
                pass
        self._dispatch      = {}
        self._header_sent   = 0
        self._header_props  = {"Content-Type" : "text/html;charset=UTF-8"}
        self._header_props  = {}
        self._header_type   = "header"
        self._cookies       = []
        self._url           = ""
        self._environ       = os.environ
        self.template_dir   = 'templates'
        self.run_mode_param = 'rm'
        self.start_mode     = ''
        self.__globals__    = {}
        self.setup()
        
    def param(self,name):
        """ returns the value of a named CGI parameter

        if the parameter isn't present, an empty string is returned.
        
        param() will always return a string. if you expect the parameter to
        be something else, you must cast it back yourself.
        """

        try:
            entry = self.form[name]
        except KeyError:
            return ""
        if type(entry) == ListType:
            return [str(v.value) for v in entry]
        else:
            return str(entry.value)
        
    def cookie(self,name):
        """ returns the value of a cookie

        if the cookie wasn't set, it returns an empty string.

        cookie() will always return a string. 
        """
        try:
            return str(self._cookies_in[name].value)
        except:
            return ""
    
    def setup(self):
        """ set up the application
        
        this method needs to be overriden. it should define the dispatch
        table and do any other necessary initialization. 
        
        """
        pass

    def prerun(self,runmode=""):
        """ runs before the actual runmode is executed.

        if this method returns false, the runmode isn't executed. this
        makes it a good place to put authentication code. if authentication
        fails, you can do a redirect from here and return false. """
        return 1
        
    def run(self):
        """ runs the application

        determines the runmode, calls the appropriate method (as set by the
        dispatch table), and returns the results, along with the proper
        http headers to the browser.
        """
        
        run_mode = self.param(self.run_mode_param) or self.start_mode
        if self._dispatch.has_key(run_mode):
            method = self._dispatch[run_mode]
        else:
            if callable(getattr(self,run_mode)):
                method = getattr(self,run_mode)
            else:
                # couldn't find a method for that runmode
                raise AttributeError, "no such runmode"
        res = ""
        if self.prerun(run_mode):
            res = method()
        else:
            res = "prerun failed and no redirect was made. this shouldn't happen"
        if self._header_type != "redirect":
            self.send_output(res)
        else:
            self.send_redirect()
        self.teardown()
        if self.req != None:
            if self._header_type == "redirect":
                return apache.HTTP_MOVED_TEMPORARILY
            else:
                return apache.OK
        else:
            return None
 
    def teardown(self):
        """ handles cleanup for the application
        
        should be overridden if something needs to happen after the 
        runmode is finished
        """
        pass
        
    def mode_param(self,name):
        """ specify which parameter to use for the run mode

        If you wish to use a parameter besides 'rm' as the run mode, 
        use this method to change it. You must call this *before* you call
        run()
        """
        
        self.run_mode_param = name
        

    def header_type(self,type):
        """ set the header type

        type must be either 'header' or 'redirect'
        """
        self._header_type = type
        
    def header_props(self,props={}):
        """ add additional HTTP headers or modify existing ones

        pass in a dictionary of key/value pairs. if any of the existing
        headers match, they will be overridden, otherwise they will be 
        added.
        """
        for k in props.keys():
            self._header_props[k] = props[k]
            
    def set_cookies(self,cookies=[]):
        """ add cookies to be sent to the browser

        pass in a list of Cookie objects 
        """
        for c in cookies:
            self._cookies.append(c)

    def set_cookie(self,name,value,**fields):
        if self.req != None:
            # make a mod_python cookie
            cookie = Cookie.Cookie(name,value)
            if fields.has_key('expires'):
                # mod_python handles times a little differently
                # we need to add the current time to the expires
                from mod_python.Cookie import time
                fields['expires'] = time.time() + fields['expires']
            for k in fields.keys():
                setattr(cookie,k,fields[k])
            self._cookies.append(cookie)
        else:
            # make a regular CGI cookie
            cookie = SimpleCookie()
            cookie[name] = value
            for k in fields.keys():
                cookie[name][k] = fields[k]
            self._cookies.append(cookie)
            
    def send_header(self):
        """ sends the http headers to the browser 
        
        this should only be called from the run() method. 
        don't call this one yourself.
        """
        if self._header_sent != 0:
            return
        if self.req == None:
            for h in self._header_props.keys():
                print "%s: %s" % (h,self._header_props[h])
            self.send_cookies()
            print ""
        else:
            # mod_python
            self.req.content_type = self._header_props["Content-Type"]
            del self._header_props["Content-Type"]
            for h in self._header_props.keys():
                self.req.headers_out[h] = self._header_props[h]
            self.send_cookies()

        self._header_sent = 1
        
    def send_redirect(self):
        """ sends a redirect header to the browser

        this should only be called from the run() method. don't call this
        one yourself.
        """
        if self._header_sent != 0:
            return
        if self.req != None:
            self.req.headers_out['location'] = self._redirect_url
            self.req.status = apache.HTTP_MOVED_TEMPORARILY
            self.send_cookies()
        else:
            print "Location: %s" % str(self._redirect_url)
            self.send_cookies()
            print ""
        self._header_sent = 1
        
    def redirect(self,url):
        """ redirects the browser to the specified url
        """
        self._header_type = "redirect"
        self._redirect_url = url

    def send_cookies(self):
        """ sends the http headers for any cookies that need to be set
        """
        if self.req != None:
            for c in self._cookies:
                Cookie.add_cookie(self.req,c)
        else:
            for c in self._cookies:
                print c

    def send_output(self,message):
        """ prints http headers and output """
        self.send_header()
        if self.req == None:
            if message != None:
               print message
        else:
            self.req.write(message)

    def referer(self):
        """ returns the HTTP_REFERER """
        if self.req != None:
            return self.req.headers_in["referer"]
        else:
            try:
                return os.environ['HTTP_REFERER']
            except KeyError:
                # no referer was set by the environment
                return ""

    def add_globals(self,data={}):
        """ set global variables for all templates """
        self.__globals__ = data

    def template(self,template_file,data={}):
        """ replaces the variables in the template with values specified in
        a dictionary.

        if the template filename ends in ".pt", it uses simpleTAL,
        otherwise, it will use the htmltmpl module.

        override this method if you want to use a different template
        library. """
        if template_file[-3:] == ".pt":
            return self.tal_template(template_file,data)
        else:
            return self.html_template(template_file,data)


    def html_template(self,template_file,data={}):
        """ replaces the variables in the template with values specified in
        a dictionary.

        uses the htmltmpl module. see the documentation for htmltmpl for more info.

        """
        from htmltmpl import TemplateManager, TemplateProcessor
        mgr = TemplateManager()
        template = mgr.prepare("%s/%s" % (self.template_dir,template_file))
        tproc = TemplateProcessor(html_escape=0)
        for key in self.__globals__.keys():
            tproc.set(key,self.__globals__[key])

        for key in data.keys():
            tproc.set(key,data[key])

        return tproc.process(template)

    def tal_template(self, filename, data={}):
        from simpletal import simpleTAL, simpleTALES
        import cStringIO
        context = simpleTALES.Context(allowPythonPath=1)

        for k in self.__globals__.keys():
            context.addGlobal(k,self.__globals__[k])

        for k in data.keys():
            context.addGlobal(k,data[k])
        try:
            # if there's a macros.pt file, we load that
            macrosfile = open("%s/macros.pt" % self.template_dir)
            macros = simpleTAL.compileXMLTemplate(macrosfile)
            macrosfile.close()
            context.addGlobal("sitemacros",macros)
        except:
            pass

        templatefile = open("%s/%s" % (self.template_dir,filename),'r')
        template = simpleTAL.compileXMLTemplate(templatefile)
        templatefile.close()
        fakeout = cStringIO.StringIO()
        template.expand(context,fakeout)
        fakeout.seek(0)
        return fakeout.read()

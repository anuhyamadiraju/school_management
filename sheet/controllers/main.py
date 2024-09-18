from odoo import http , _, SUPERUSER_ID
from odoo.addons.portal.controllers.portal import pager as portal_pager, CustomerPortal
import base64
import io
from werkzeug.utils import redirect
from datetime import datetime,date,timedelta
import calendar
# import datetime
from odoo import http
from odoo.http import request
from odoo.osv.expression import AND ,OR
import dateutil.relativedelta
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.tools import groupby as groupbyelem
from operator import itemgetter
class EnquiryController(http.Controller):

    @http.route(['/enquiry/form'], type='http', auth="public", website=True)
    def enquiry_form(self, **post):
        return request.render("sheet.enquiry_form", {})


    

    @http.route(['/enquiry/form/submit'], type='http', auth="public", website=True, csrf=False)
    def enquiry_form_submit(self, **post):
        
        name = post.get('name')
        age = post.get('age')
        class_name = post.get('class_name')
        student_gender = post.get('student_gender')
        dob = post.get('dob')
        student_address = post.get('student_address')
        parent_name = post.get('parent_name')
        phone_number = post.get('phone_number')
        parent_occupation = post.get('parent_occupation')

        
        if name and parent_name and phone_number:
            enquiry = request.env['enquiry'].sudo().create({
                'name': name,
                'class_name': class_name,
                'gender': student_gender,
                'dob': dob,
                'age': age,
                'address': student_address,
                'parent_name': parent_name,
                'phone_number': phone_number,
                'parent_occupation': parent_occupation,
                'state': 'draft' 
            })

            
            return request.render("sheet.enquiry_form_success", {'enquiry_id': enquiry.enquiry_id})

    @http.route(['/search/enquiry'], type='http', auth="public", website=True)
    def search_enquiry(self, **kw):
        
        user_id = request.env.user.id

        
        Enquiry = request.env['enquiry'].sudo()
        enquiries = Enquiry.search([('create_uid', '=', user_id)])  # Filter by the creator ID

        
        if not enquiries:
            
            return request.render('sheet.no_enquiries_found')

        
        return request.render('sheet.enquiry_search_page', {
            'enquiries': enquiries,
        })

    @http.route(['/enquiry/detail/<int:enquiry_id>'], type='http', auth="public", website=True)
    def enquiry_detail(self, enquiry_id, **kw):
       
        Enquiry = request.env['enquiry'].sudo().browse(enquiry_id)
        if not Enquiry.exists():
            return request.not_found()  


        return request.render('sheet.enquiry_detail_page', {
            'enquiry': Enquiry,
        })

class AuthController(http.Controller):

    @http.route('/web/login', type='http', auth='public', website=True)
    def web_login(self, redirect=None, **kw):
        if request.httprequest.method == 'POST':
            
            login = request.params.get('login')
            password = request.params.get('password')
            uid = request.session.authenticate(request.session.db, login, password)
            if uid:
                
                return request.redirect(redirect or '/custom-page')

        
        values = {
            'redirect': redirect,
            'signup_enabled': True,  
        }
        return request.render('web.login', values)